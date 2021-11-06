# makeh2kit
This is a simple dumb script that creates Hydrogen drumkits

## Dependencies

 - Python 3
 - `strictyaml`, via `$ pip3 install strictyaml`

## Motivating example

Say you have a directory full of samples with some arbitrary structure. You
want to make some of them into a Hydrogen drumkit. You don't want to hand-edit
a bunch of XML and assemble a tarfile.

Just make a YAML file listing out the filenames you want like this:

```
- kick 1.wav
- snare 7.wav
- wacky scratch noise.wav
```

... then run the script:

```
$ python3 makeh2kit.py -i mykit.yml -o mykit -s samples misc/more_samples
```

And the script spits out "mykit.h2drumkit", which you can import.

If you find yourself doing this a lot I guess set the execute bit and copy it
into your `PATH`.

## Examples

This kind of stuff should basically work, it's minimally tested.

### Simple

Just make a list of the filenames

```
- Kick 1.wav
- Kick 2.wav
- Snare 7.wav
```

### Attributes on instruments

To set attributes on instruments use a form like this.

```
- name: Crashy Boi
  filename: Crash Cymbal 11.wav
- name: Orchestra Hit L
  filename: Orchestra Hit.wav
  pan_L: 1
  pan_R: 0
- name: Orchestra Hit R
  filename: Orchestra Hit.wav
  pan_L: 0
  pan_R: 1
```

For a list of attributes I've seen in XML examples online look at
`_default_values` in the `Instrument` class. The code will let you pass almost
anything you want, no guarantee Hydrogen will accept it. In Hydrogen's XML
format you have to list filenames down in the layers; I accept "filename" on
instrument descriptions to create a single-layer instrument to make it easier.

### Multiple layers per instrument

Layers allow different samples to be used at different velocity levels. That
specification looks like this:

```
- name: Sophisticated Crash
  layers:
    - filename: Quiet crash.wav
      min: 0
      max: 0.3
    - filename: medium crash.wav
      min: 0.3
      max: 0.6
    - filename: loud crash.wav
      min: 0.6
      max: 0.9
    - filename: FUCKIN WHALIN ON IT.wav
      min: 0.9
      max: 1
```

For a list of attributes I've seen in XML examples online look at
`_default_values` in the `Layer` class. As above, no guarantee Hydrogen will
accept something just because the script allows it :-).

### Mix and match instrument formats

I haven't tried giving Hydrogen an image file, YMMV.

```
- just a filename.wav

- name: A quiet triangle
  volume: .1
  filename: triangle.wav

- name: A drum seen and not heard
  volume: 0
  layers:
    - filename: background.jpg
      min: 0
      max: 0.5
    - filename: snare drum.png
      min: 0.5
      max: 1
```

## Q and As

 - **How is case handled?** Short answer: it's case-insensitive. Medium answer:
it searches all search dirs for exact match, then tries case-insensitive
match. Long answer: I am vaguely aware that calling `.lower()` on both sides of
a string comparison isn't totally correct, and although it would be funny for a
script of this size to use proper ICU casefolding I haven't got around to it.

 - **Why Python?** I considered shell but you know how it is, if it's easier in
shell it's a little easier, if it's harder in shell it's a lot harder. If this
was a few years ago it would have been Perl.

 - **Why YAML?** I was going to make the input just a textfile with one
filename per line but then I thought I might as well add optional support
for attributes.  Rather than invent a new dumb format, I chose an existing
format that I don't know much about but am going to need to learn for some work
stuff.

 - **Literally why bother with a Makefile?** That was just so I could do `:make
lint` in vim and have the cursor jump straight to my errors. I'm a simple
man with bad taste.

 - **Ew, xml.etree?** Whatever, it works. I'm a simple man with bad taste.

 - **Your code is shit.** Always has been.

