"""
Routines for converting and manipulating files.
"""
# System dependencies
import os
import subprocess
import sys

# My dependencies
import util as u


class Convert():
    """Base class for converters."""
    def ttb(func, output, depends, *args, **kwargs):
        """func is a conversion function to run on the args and kwargs to produce the output.
    
        depends is a string or list of filespecs

        **kwargs are whatever the func calls for.

        output is a filespec.  We run u.time_to_build on the output
        and depends and if it comes back saying the output file is out
        of date, we rebuild it from the depends, args and kwargs by
        calling the func.

        """
        if u.time_to_build(u.str2list(depends), output):
            return func(output, depends, *args, **kwargs)

    def replace_ext(self, fname, ext):
        """Chops off extension of fname and replaces it with ext, returns
        result."""
        return os.path.splitext(fname)[0] + ext

class PDF(Convert):
    def __init__(self, quiet=False):
        self.quiet = quiet

    def pages(self, fname):
        cmd = "pdfinfo {0} | grep Pages".format(fname)
        return u.call(cmd)[0].split(' ',1)[1].strip()

    def dvips(self, output, depend):
        cmd = "dvips -o {0} {1}".format(output, depend)
        if not self.quiet: print cmd
        os.system(cmd)

    def ps2pdf(self, output, depend):
        cmd = "ps2pdf {1} {0}".format(output, depend)
        if not self.quiet: print cmd
        os.system(cmd)

    def pdflatex(self, output, depends, binary="pdflatex", clean=True):
        "Convert latex to pdf using pdflatex"
        depends = u.str2list(depends)
        cmd = '{2} -jobname "{0}" "{1}"'.format(output, '" "'.join(depends), binary)
        if not self.quiet: print cmd
        os.system(cmd)
        if clean:
            os.system("rm -f "+" ".join(map(lambda x: self.replace_ext(output, x), [".aux", ".log", ".out"])))

    def latex(self, output, depends):
        "Convert latex to pdf using latex, dvips and ps2pdf"
        self.pdflatex(self.replace_ext(output, ".dvi"), depends, "latex")
        self.dvips(self.replace_ext(output, ".ps"), self.replace_ext(output, ".dvi"))
        self.ps2pdf(self.replace_ext(output, ".pdf"), self.replace_ext(output, ".ps"))

    def join(self, fname, files):
        files = u.str2list(files)
        cmd = 'gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="{0}" {1}'.format(fname, " ".join(files))
        if not self.quiet: print cmd
        os.system(cmd)

    def burst(self, fname):
        cmd = 'pdftk burst ' + fname
        if not self.quiet: print cmd
        os.system(cmd)

