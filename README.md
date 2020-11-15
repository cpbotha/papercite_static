`papercite_static` is my attempt at bringing some of the magic of the Wordpress
plugin papercite to the static blog scene.

It takes any text file with special embedded `papercite()` commands in the form
of HTML comments, and then expands each of those `papercite()` invocations to a
bibliography rendered from bibtex files.

See below for a usage example.

## Warning

This is a 100% hack to scratch my own itch, which I'm putting here in case
someone else finds it useful.

- It may not work for you. In that case, read the source to `genbib.py` and try
  to figure out why. I will be grateful if you document your solution as a
  github issue.
- Please don't report any bugs or submit any feature requests, unless they're
  actually work-arounds or solutions that could be helpful to other users.
- If you like, you can try to make a PR. I might merge it. Or not.

## Example

The source of [the publications page on my personal
website](https://charlbotha.com/publications/), called `_index.md.in` inside of
a Hugo hierarchy, looks something like this:

``` markdown
Some introductory text here.

## Book

<!-- papercite("cpbotha.bib", keys=["preim_visual_2013"]) -->

This is the standard text for the field of Medical Visualization. Read more
about the book by going to [medvisbook.com](http://medvisbook.com/).

## Theses
<!-- papercite("cpbotha.bib", keys=["botha_techniques_2005", "botha_-line_1999"]) -->

Don't be fooled by Zotero's exporter: I wrote one Ph.D. thesis on medical
visualization and one M.Sc. thesis on froth. Yes froth.

## Journal Articles

<!-- papercite("cpbotha.bib", allow=['article'], year_group=True) -->

## Conference proceedings and everything else

<!-- can't exclude book, because in Zotero our editorship of vcbm proceedings is a book -->
<!-- papercite("cpbotha.bib", deny=['article', 'phdthesis'], year_group=True) -->
```

### Invoking the script

- Invoke `python genbib.py _index.md.in index.md` to insert bibliographies.
- BibTeX `.bib` file is relative to the `.md.in`.
- Attachments (PDFs or other fulltexts specified in the BibTeX `file` field)
  will be looked for relative to the bibfile.

I usually keep all of the input files, and the attachments, in the same Hugo
directory, from where I run the script, and then re-generate the Hugo website.

You should be able to adapt for your static website generator of choice.
