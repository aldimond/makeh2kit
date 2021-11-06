#!/usr/bin/env python3

import argparse
import copy
import logging
import os
import os.path
import shutil
import tarfile
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

import strictyaml # type: ignore


# Allowed types for XML text data
_ALLOWED_TEXT_TYPES = str, int, float


def _check_value_types(values: Dict[str, Any], ident: str) -> None:
    for k, v in values.items():
        if not any(isinstance(v, t) for t in _ALLOWED_TEXT_TYPES):
            raise Exception(f"Illegal value: {repr(v)} for '{k}' tag in {ident}")

class Layer:
    values: Dict[str, Any]

    _default_values = {
            "min": 0,
            "max": 1,
            "gain": 1,
            "pitch": 0,
            }

    def __init__(self, filename: str, values: Optional[Dict[str, Any]] = None):
        self.values = copy.deepcopy(Layer._default_values)
        self.values["filename"] = filename
        if values:
            self.values.update(values)

        _check_value_types(self.values, self._ident())

    def to_xml(self) -> Element:
        result = Element("layer")
        for k, v in self.values.items():
            sub = SubElement(result, k)
            sub.text = str(v)
        return result

    def _ident(self) -> str:
        return f"Layer ({self.values['filename']})"


class Instrument:
    id: int
    layers: List[Layer]
    values: dict

    _default_values = {
            "volume": 1,
            "isMuted": "false",
            "pan_L": 1,
            "pan_R": 1,
            "randomPitchFactor": 0,
            "filterActive": "false",
            "filterCutoff": 1,
            "filterResonance": 0,
            "Attack": 0,
            "Decay": 0,
            "Sustain": 1,
            "Release": 1000,
            }

    def __init__(self, id: int, data: Any):
        self.values = copy.deepcopy(Instrument._default_values)
        self.values["id"] = id

        if isinstance(data, str):
            self.values["name"] = data
            self.layers = [Layer(data)]
        elif isinstance(data, dict):
            self.values.update(data)

            if not "name" in self.values:
                raise Exception(f"{self._ident()} missing name")

            if "filename" in self.values:
                self.layers = [Layer(self.values.pop("filename"))]
            elif "layers" in self.values:
                layervals = self.values.pop("layers")
                if not isinstance(layervals, list):
                    raise Exception("layers not a list")
                self.layers = list()
                for l in layervals:
                    if not "filename" in l:
                        raise Exception(f"Layer in {self._ident()} missing filename")
                    self.layers.append(Layer(l["filename"], l))
            else:
                raise Exception(f"No filename/layers for {self._ident()}")
        else:
            raise Exception(f"{self._ident()} neither a mapping nor a string!")

        _check_value_types(self.values, self._ident())
  

    def _ident(self) -> str:
        r = "Instrument #{self.values.get('id')}"
        if "name" in self.values:
            r += f" ({self.values['name']})"
        return r

    def to_xml(self) -> Element:
        result = Element("instrument")
        for k, v in self.values.items():
            sub = SubElement(result, k)
            sub.text = str(v)
        for l in self.layers:
            result.append(l.to_xml())
        # I don't know what this is for or what the format is :-/
        SubElement(result, "exclude")
        return result


def find_filepath(root: str, target: str, ignorecase: bool) -> Optional[str]:
    visited_dirs = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=True):
        # Avoid symlink loops
        realdir = os.path.realpath(dirpath)
        if realdir in visited_dirs:
            logging.warning(f"Already visited {dirpath} ({realdir}), skipping")
            dirnames.clear()
            continue
        visited_dirs.add(realdir)

        for filename in filenames:
            match = filename.lower() == target.lower() if ignorecase else filename == target
            if match:
                return os.path.join(dirpath, filename)

    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input file (drumkit description, YAML", required=True)
    parser.add_argument("-o", help="Output h2drumkit name", required=True)
    parser.add_argument("-s", help="Sample search dirs", type=str, nargs="+")
    parser.add_argument("-n", help="Drumkit name (by default same as -o)")
    parser.add_argument("--info", help="Info string for drumkit")

    args = parser.parse_args()

    if not args.n:
        args.n = args.o

    if not args.o.endswith(".h2drumkit"):
        args.o += ".h2drumkit"

    # Set up outer document
    doc = Element("drumkit_info")
    SubElement(doc, "name").text = args.n

    with open(args.i, encoding="utf-8") as infile:
        kitdesc = strictyaml.load(infile.read()).data

    if not isinstance(kitdesc, list):
        raise Exception("drumkit description should contain a YAML sequence")

    instruments = [Instrument(i, kitdesc[i]) for i in range(len(kitdesc))]

    with TemporaryDirectory() as tempdir:
        for instrument in instruments:
            for layer in instrument.layers:
                filename = layer.values["filename"]
                found = None

                for searchdir in args.s:
                    found = find_filepath(searchdir, filename, False)
                    if found:
                        break

                if not found:
                    for searchdir in args.s:
                        found = find_filepath(searchdir, filename, True)
                        if found:
                            break
                
                if not found:
                    raise Exception(f"Could not find {filename}")

                shutil.copyfile(found, os.path.join(tempdir, filename))

        SubElement(doc, "instrumentList").extend(inst.to_xml() for inst in instruments)

        with open(os.path.join(tempdir, "drumkit.xml"), mode="w", encoding="utf-8") as f:
            f.write(ElementTree.tostring(doc, encoding="unicode"))

        with tarfile.open(args.o, "w:gz") as tf:
            tf.add(tempdir, arcname=args.n)

