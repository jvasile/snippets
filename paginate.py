#!/usr/bin/env python

# System dependencies
import os
import sys

# My dependencies
from doconvert import PDF
import util as u

class Paginate():
    defaults = {
        'lhead':'',
        'chead':'',
        'rhead':'',
        'lfoot':'',
        'cfoot':'',
        'rfoot':'',
        'starting_page':1,
        'landscape':False,
    }

    """Class to take a PDF and add page numbers to it."""
    def __init__(self, **kwargs):
        """Pass in defaults for all the other functions."""
        self.defaults = dict(self.defaults.items() + kwargs.items())

        if (not self.defaults['lfoot']
            and not self.defaults['cfoot']
            and not self.defaults['rfoot']):
            self.defaults['rfoot'] = r"\thepage"

    def latex(self, pdf_fname, **kwargs):
        pdf_fname = pdf_fname.replace(" ", "\\space ")
        opts = dict(self.defaults.items() + kwargs.items())
        opts['pdf_fname'] = pdf_fname
        opts['landscape'] = "true" if opts['landscape'] else "false"
        print opts
        return r"""\documentclass{{article}}
\setcounter{{page}}{{{first_page_num}}}
\usepackage[margin=.5in]{{geometry}}
\usepackage{{pdfpages}}
\usepackage{{fancyhdr}}
\fancyhf{{}}
\renewcommand{{\headrulewidth}}{{0pt}}

\setboolean{{@twoside}}{{false}}

\begin{{document}}

\lhead{{\vspace{{4mm}} {lhead}}}
\chead{{\vspace{{4mm}} {chead}}}
\rhead{{\vspace{{4mm}} {rhead}}}
\lfoot{{{lfoot}}}
\cfoot{{{lfoot}}}
\rfoot{{{rfoot}}}

\includepdf[landscape={landscape}, pages=-, offset=0 0, pagecommand={{\thispagestyle{{fancy}}}}]{{{pdf_fname}}}

\end{{document}}
""".format(**opts)

    def paginate(self, out_fname, in_fname, **kwargs):
        """Set kwargs['clean'] = True to cause deletion of aux, log and out files."""
        if not 'clean' in kwargs:
            kwargs['clean'] = True

        c = PDF()
        with u.TemporaryDirectory() as td:
            lname =  os.path.join(td, os.path.basename(c.replace_ext(out_fname, ".tex")))
            with open(lname, 'w') as OUTF:
                OUTF.write(self.latex(in_fname, **kwargs))
            c.pdflatex(c.replace_ext(out_fname, ""), lname)
        if kwargs['clean']:    
            os.system("rm -f "+c.replace_ext(out_fname, ".aux"))
            os.system("rm -f "+c.replace_ext(out_fname, ".log"))
            os.system("rm -f "+c.replace_ext(out_fname, ".out"))


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Add headers and footers to a PDF.',
                                     epilog="Hints: Putting \\thepage in footers will print the page number on each page. Footers and headers sometimes look nice wrapped in \ital{}.")
    parser.add_argument("input", help="The PDF in need of headers and footers.")
    parser.add_argument("output", help="The filename to write to.")
    parser.add_argument('--lhead', action='store', help='left header text', default="")
    parser.add_argument('--chead', action='store', help='center header text', default="")
    parser.add_argument('--rhead', action='store', help='right header text', default="")
    parser.add_argument('--lfoot', action='store', help='left footer text', default="")
    parser.add_argument('--cfoot', action='store', help='center footer text', default="")
    parser.add_argument('--rfoot', action='store', help='right footer text', default="")
    parser.add_argument('--first-page-num', action='store', help='lowest page number', default=1)
    parser.add_argument('--landscape', action='store_true', help='rotate the page', default=False)

    args = parser.parse_args()
    p = Paginate()
    p.paginate(args.output, args.input, **(args.__dict__))

if __name__ == "__main__":
    main()
