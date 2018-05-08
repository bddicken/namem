# namem

Generate an quiz given a roster PDF file.
This script specifically works with PDF roster files generated via UAccess for courses at the University of Arizona.
The steps to use this are:

* Download the PDF roster file for your course.
* Run `namem.py`.
  You'll need to specify at least two arguments:
  Tell `namem.py` where your roster PDF file is with `--roster`.
  Tell `namem.py` a directory to generate the quiz in with `--out`.
* Once the script has finished running, navigate to the directory that you generated the namem quiz to, and open up `index.html` in a web-browser.

For FERPA reasons, you may want to stick to only using this quiz locally, rather than actually hosting on a public-facing web-server.

## Dependencies

Requires a few standard python modules: `os`, `shutil`, and `argparse`.
It also requires some "extra" modules: `numpy`, `PIL`, and `wand`.

## Mac
Even after installing PIL and wand on Mac, you might still need to specify the `MAGICK_HOME` directory for the module to work properly.
Something along the lines of:
```
export MAGICK_HOME=/usr/local/Cellar/imagemagick\@6/6.9.9-41/
```
