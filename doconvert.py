"""
Routines for converting and manipulating files.
"""
# System dependencies
import os

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

    def pdflatex(self, output, depends):
        depends = u.str2list(depends)
        cmd = 'pdflatex -jobname "{0}" "{1}"'.format(output, '" "'.join(depends))
        print cmd
        os.system(cmd)

    def pdf_join(self, fname, files):
        files = u.str2list(files)
        cmd = 'gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="{0}" {1}'.format(fname, " ".join(files))
        os.system('gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="{0}" {1}'.format(fname, " ".join(files)))



