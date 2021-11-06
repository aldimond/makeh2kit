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
$ python3 makeh2kit.py -i mykit.yml -o mykit -s samples -s misc/more_samples
```

And the script spits out "mykit.h2drumkit", which you can import.

If you find yourself doing this a lot I guess set the execute bit and copy it
into your `PATH`.

You should also be able to specify more details with a deeper format if you
want, I'm not documenting it yet because I haven't tested it yet, also I
haven't learned enough YAML to write an example yet :-P.

## Q and As

 - **Why Python?** I considered shell but you know how it is, if it's easier in
shell it's a little easier, if it's harder in shell it's a lot harder. If this
was a few years ago it would have been Perl.

 - **Why YAML?** I was going to make the input just a textfile with one
filename per line but then I thought I might as well add optional support
for attributes.  Rather than invent a new dumb format, I chose an existing
format that I don't know much about but am going to need to learn for some work
stuff.

 - **Ew, xml.etree?** Whatever, it works.

 - **Your code is shit.** Always has been.

