"""Just some random snippets I find useful in multiple places.  I
typically do "import util as u" and then invoke these as u.foo.

Copyright 2016 James Vasile <james@jamesvasile.com>
Published under the terms of the Affero GPL, version 3 or later

"""

from __future__ import print_function

import os
import string
import sys

import util as u # yeah, this is weird but REASONS

def err(msg):
    if not msg.endswith("\n"):
        msg += "\n"
    sys.stderr.write(msg)
    sys.exit()


def fetch_json(fname):
    """Read a json document from a file, minify to remove comments (json
    parser pukes b/c comments aren't spec), return data structure
    matching document.

    """
    import simplejson as json
    from json_minify import json_minify as minify # https://github.com/getify/JSON.minify/tree/python
    from collections import OrderedDict
    return json.loads(minify(u.slurp(os.path.expanduser(fname))),
                      object_pairs_hook=OrderedDict)

def make_logger(name, level):
    "level is a string (INFO, DEBUG, WARN, ERROR, CRITICAL)"
    import logging

    #create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    #create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    #create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch
    ch.setFormatter(formatter)
    #add ch to logger
    logger.addHandler(ch)
    return logger

def randpass(size=12, chars=string.letters + string.digits):
    import random
    return ''.join(random.choice(chars) for l in range(size))

def slurp(fname, split=False):
    with open(fname) as INF:
        data = INF.read()
        if not split:
            return data
    return data.split("\n")

def str2list(s):
    return [s] if isinstance(s, basestring) else s

def time_to_build(files, target):
    """files is a list of files.  It could also be a string with a
    filename if the list length is 1

    Return True if any of the files are newer than the target or if the
    target is missing.  Raise error if any of the files are missing.

    """

    files = u.str2list(files)

    # Make sure files exist
    for f in files:
        if not os.path.exists(f):
            raise OSError(2, "No such file or directory", f)

        # If the target doesn't exist, we should build it.
        if not os.path.exists(target):
            return True

        # If the newest doc isn't our target, we should rebuild
        return (reduce( (lambda o,n: o if os.stat(o)[8] > os.stat(n)[8] else n),
                        files + [target]) 
                != target)




class TemporaryDirectory(object):
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed.
    """

    def __init__(self, suffix="", prefix="tmp", dir=None):
        from tempfile import mkdtemp
        self._closed = False
        self.name = None # Handle mkdtemp raising an exception
        self.name = mkdtemp(suffix, prefix, dir)

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.name)

    def __enter__(self):
        return self.name

    def cleanup(self, _warn=False):
        if self.name and not self._closed:
            try:
                self._rmtree(self.name)
            except (TypeError, AttributeError) as ex:
                # Issue #10188: Emit a warning on stderr
                # if the directory could not be cleaned
                # up due to missing globals
                if "None" not in str(ex):
                    raise
                print("ERROR: {!r} while cleaning up {!r}".format(ex, self,),
                      file=_sys.stderr)
                return
            self._closed = True
            if _warn:
                self._warn("Implicitly cleaning up {!r}".format(self),
                           ResourceWarning)

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def __del__(self):
        # Issue a ResourceWarning if implicit cleanup needed
        self.cleanup(_warn=True)

    # XXX (ncoghlan): The following code attempts to make
    # this class tolerant of the module nulling out process
    # that happens during CPython interpreter shutdown
    # Alas, it doesn't actually manage it. See issue #10188
    import warnings as _warnings
    import os as _os
    _listdir = staticmethod(_os.listdir)
    _path_join = staticmethod(_os.path.join)
    _isdir = staticmethod(_os.path.isdir)
    _islink = staticmethod(_os.path.islink)
    _remove = staticmethod(_os.remove)
    _rmdir = staticmethod(_os.rmdir)
    _warn = _warnings.warn

    def _rmtree(self, path):
        # Essentially a stripped down version of shutil.rmtree.  We can't
        # use globals because they may be None'ed out at shutdown.
        for name in self._listdir(path):
            fullname = self._path_join(path, name)
            try:
                isdir = self._isdir(fullname) and not self._islink(fullname)
            except OSError:
                isdir = False
            if isdir:
                self._rmtree(fullname)
            else:
                try:
                    self._remove(fullname)
                except OSError:
                    pass
        try:
            self._rmdir(path)
        except OSError:
            pass
