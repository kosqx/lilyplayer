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


class FunctionWithParams(object):
    def __init__(self, fun, *args):
        self.fun = fun
        self.args = args

    def __call__(self, *other):
        self.fun(*(self.args + other))

class File(object):
    def __init__(self, path):
        if isinstance(path, basestring):
            self.path = os.path.abspath(path)
        else:
            self.path = os.path.join(os.path.expanduser(path[0]), *path[1:])
            
    def exists(self):
        return os.path.exists(self.path)
    
    def makedirs(self):   
        dir = os.path.dirname(self.path)
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    def read(self, offset=None, size=None):
        f = open(self.path)
        if offset is not None:
            f.seek(offset)
        if size is None:
            d = f.read()
        else:
            d = f.read(size)
        f.close()
        return d
    
    def write(self, data):
        self.makedirs()
        f = open(self.path, 'w')
        f.write(data)
        f.close()


class Struct(object):
    """
    Simple structure like object, used in place simple dicts.
    """
    class StructIter(object):
        def __init__(self, struct):
            self._iter = iter(struct)
        def next(self):
            while True:
                val = self._iter.next()
                if not val.startswith('_'):
                    return val
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
    
    def __getitem__(self, key):
        return self.__dict__[key]
    
    def __contains__(self, item):
        return item in self.__dict__
    
    def __iter__(self):
        return Struct.StructIter(self.__dict__)
    
    def __repr__(self):
        args = ['%s=%r' % (i, self.__dict__[i]) for i in self.__dict__ if not i.startswith('_')]
        return 'Struct(' + ', '.join(args) + ')'
        
    def _keys(self):
        return [i for i in self.__dict__ if not i.startswith('_')]
        

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


def levenshtein_distance(a,b):
    "Calculates the Levenshtein distance between a and b."
    # Orginal source: http://hetland.org/coding/python/levenshtein.py
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
        
    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add    = previous[j] + 1
            delete = current[j - 1] + 1
            change = previous[j - 1] + int(a[j - 1] != b[i - 1])
            
            current[j] = min(add, delete, change)
            
    return current[n]

def reduce_fraction(a,b):
    d = 2
    while d <= min(a,b):
        while a % d == 0 and b % d == 0:
            a, b = a / d, b / d
        d += 1
    return a,b


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

