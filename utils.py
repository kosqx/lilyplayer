#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Copyright (C) 2007  Krzysztof Kosyl <krzysztof.kosyl@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

"""
    Many simple tools but usefull in many places.
"""

import re
import os.path
import unittest

# ToDo: try remove this import and create own simple procedure
from xml.sax.saxutils import quoteattr
from StringIO import StringIO

def clamp(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value

def int_or(value, default=None):
    try:
        return int(value)
    except:
        return default

def at_index_or(vector, index, default=None):
    try:
        return vector[index]
    except:
        return default


class File(object):
    def __init__(self, path):
        if isinstance(path, basestring):
            self.path = os.path.abspath(path)
        else:
            self.path = os.path.join(os.path.expanduser(path[0]), *path[1:])
    
    def read(self):
        f = open(self.path)
        d = f.read()
        f.close()
        return d
    
    def write(self, data):
        f = open(self.path)
        f.write(data)
        f.close()


class Null(object):
    """ Null objects always and reliably "do nothing." """
    # optional optimization: ensure only one instance per subclass
    # (essentially just to save memory, no functional difference)
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = type.__new__(cls, *args, **kwargs)
        return cls._inst
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __repr__(self): return "Null( )"
    def __nonzero__(self): return False
    def __getattr__(self, name): return self
    def __setattr__(self, name, value): return self
    def __delattr__(self, name): return self


def makepath(path):

    """ creates missing directories for the given path and
        returns a normalized absolute version of the path.

    - if the given path already exists in the filesystem
      the filesystem is not modified.

    - otherwise makepath creates directories along the given path
      using the dirname() of the path. You may append
      a '/' to the path if you want it to be a directory path.
      
    Example:
      file = open(makepath('/tmp/dir/hallo'), 'w')

    from holger@trillke.net 2002/03/18
    """

    from os import makedirs
    from os.path import normpath,dirname,exists,abspath

    dpath = normpath(dirname(path))
    if not exists(dpath):
        makedirs(dpath)
    return normpath(abspath(path))

def embedded_numbers(s):
    re_digits = re.compile(r'(\d+)')
    pieces = re_digits.split(s)
    #pieces[1::2] = map(int, pieces[1::2])   
    pieces[1::2] = [(int(i), len(i)) for i in pieces[1::2]]
    return pieces

def asdf(da):
    result = list(da)
    result[1::2] = ["%.*d" % (i[1], i[0]) for i in da[1::2]]
    
    return ''.join(result)

if __name__ == '__main__':
    unittest.main()
