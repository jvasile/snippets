"""Just some random snippets I find useful in multiple places.  I
typically do "import util as u" and then invoke these as u.foo.

Copyright 2016 James Vasile <james@jamesvasile.com>
Published under the terms of the Affero GPL, version 3 or later

"""

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



def slurp(fname, split=False):
    with open(fname) as INF:
        data = INF.read()
        if not split:
            return data
    return data.split("\n")

def randpass(size=12, chars=string.letters + string.digits):
    import random
    return ''.join(random.choice(chars) for l in range(size))

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
            raise os.OSError.FileNotFoundError

        # If the target doesn't exist, we should build it.
        if not os.path.exists(target):
            return True

        # If the newest doc isn't our target, we should rebuild
        return (reduce( (lambda o,n: o if os.stat(o)[8] > os.stat(n)[8] else n),
                        files + [target]) 
                != target)
