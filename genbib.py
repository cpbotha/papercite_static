"""papercite_static

Convert embedded papercite() commands in markdown files to expanded bibliographies.

Copyright 2020 by Charl P. Botha <info@charlbotha.com> under the 3-clause BSD license
"""

from functools import lru_cache
import os
import re
import sys
from typing import List, Optional, Tuple

import pybtex.database
from pybtex.database import BibliographyData, Entry

from pybtex.style.formatting.plain import Style


from pybtex.backends.markdown import Backend, SPECIAL_CHARS
# in html and markdown backends, the newblock symbol, which gets inserted between all nodes, is transformed to \n
# we change this to ' '
Backend.symbols['newblock'] = ' '
# also, the escaped \. is not helping, so we remove that from the list of escaped chars

del SPECIAL_CHARS[SPECIAL_CHARS.index('.')]
del SPECIAL_CHARS[SPECIAL_CHARS.index('-')]

style = Style()


def format_and_maybe_link(entry: Entry, bib_dir: str) -> str:
    # name:filename;name:filename;...
    pdf_link = None
    ff = entry.fields.get('file', None)
    if ff is not None:
        files = ff.split(';')
        for f in files:
            # ct is sometimes the content-type e.g. application/pdf
            name, fn, *ct = f.split(':')
            if not os.path.isabs(fn) and fn.lower().endswith('pdf') and os.path.exists(os.path.join(bib_dir, fn)):
                # we only check if relative paths end with PDF
                pdf_link = fn

    # https://docs.pybtex.org/api/styles.html#style-api
    md = style.format_entry(None, entry).text.render_as('markdown')
    if pdf_link is not None:
        md += f' <a href="{pdf_link}" title="PDF document for {entry.key}"><img src="pdf.svg" style="height: 1em;" /></a>'

    return md


@lru_cache(maxsize=64)
def get_parsed_bib(filename: str) -> Tuple[BibliographyData, str]:
    bib_data: BibliographyData = pybtex.database.parse_file(filename, "bibtex")
    bib_dir = os.path.dirname(filename)
    return bib_data, bib_dir


# group entries by year descending
def papercite(file: str,
              keys: Optional[List[str]] = None, allow: Optional[List[str]] = None, deny: Optional[List[str]] = None,
              year_group: bool = False):

    bib_data, bib_dir = get_parsed_bib(file)

    entries = bib_data.entries

    if keys is None:
        keys = entries.keys()
        if allow is not None:
            # if we have an allowed list, only let those come through
            keys = [key for key in keys if entries[key].type in allow]

        if deny is not None:
            # if we have a deny list, take those out
            keys = [key for key in keys if entries[key].type not in deny]

        # sort these keys in reverse chrono
        keys.sort(key=lambda k: entries[k].fields.get('year'), reverse=True)

    output_lines = []

    def render_keys(keys):
        # this should happen per group
        for key in keys:
            md = format_and_maybe_link(entries[key], bib_dir)
            output_lines.append(f'- <a id="{key}"></a> {md}')

    def render_group(name, keys):
        output_lines.append(f"\n### {name}")
        render_keys(keys)

    if year_group:
        # first group is the first year in the whole list
        grp_year = entries[keys[0]].fields.get('year')
        grp_keys = []

        for key in keys:
            y = entries[key].fields.get('year')
            if y == grp_year:
                grp_keys.append(key)

            else:
                # we have hit a new year!
                if grp_keys:
                    # if there's anything in the existing group, render it
                    render_group(grp_year, grp_keys)

                # set the new year, and seed it with this current publication
                grp_year = y
                grp_keys = [key]

        # special case: the last item in the list was the first and only item of a new group
        if len(grp_keys) == 1:
            render_group(grp_year, grp_keys)

    else:
        render_keys(keys)

    return "\n".join(output_lines)


pc_re = re.compile(r'<!--\s*papercite\((.*)\)\s*-->')


def transform_md(fn_in, fn_out):
    """Read fn_in .md.in file and generate fn_out .md output with bibliographies."""
    with open(fn_in) as f_in, open(fn_out, 'w', encoding='utf-8') as f_out:
        # we change directory to where the md.in file finds itself
        # path to bibfile as specified in papercite statements should be relative to that
        # attachments will be looked for relative to bibfile
        os.chdir(os.path.dirname(os.path.abspath(fn_in)))

        for line in f_in:
            mo = pc_re.search(line)
            if mo:
                pcs = eval(f"papercite({mo.group(1)})")
                f_out.write(pcs)
                f_out.write("\n")

            else:
                f_out.write(line)


if __name__ == '__main__':
    transform_md(sys.argv[1], sys.argv[2])

