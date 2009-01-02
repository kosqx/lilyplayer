#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Copyright (C) 2008  Krzysztof Kosyl <krzysztof.kosyl@gmail.com>

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

import re
from play_time import Time

#####################################################################
# Arguments types

class PrefixArg(object):
    def __init__(self, values):
        if isinstance(values, dict):
            self.values = [(i, values[i]) for i in sorted(values.keys())[::-1]]
        else:
            self.values = [(i, i) for i in values]

    def process(self, args):
        arg = args[0]
        for prefix, val in self.values:
            if arg.startswith(prefix):
                return val, [arg[len(prefix):]] + args[1:]
        raise 'no prefix'

class SimpleArg(object):
    def process(self, args):
        return self.parse(args[0]), args[1:]

class FloatArg(SimpleArg):
    def __init__(self, min_=None, max_=None):
        self.min_ = min_
        self.max_ = max_
        
    def parse(self, text):
        #print self.min_, self.max_
        multi = 1.0
        if text.endswith('%'):
            multi = 0.01
            text = text[:-1]
        value = float(text) * multi
        if self.min_ is not None and value < self.min_:
            raise 'too small'
        if self.max_ is not None and value > self.max_:
            raise 'too big'
        return value
        
class IntArg(SimpleArg):
    def __init__(self, min_=None, max_=None):
        self.min_ = min_
        self.max_ = max_
        
    def parse(self, text):
        #print self.min_, self.max_
        value = int(text)
        if self.min_ is not None and value < self.min_:
            raise 'too small'
        if self.max_ is not None and value > self.max_:
            raise 'too big'
        return value


class TimeArg(SimpleArg):
    def __init__(self):
        self.regexp = '((\d*:)?\d*:)?\d*(.\d*)'
        
    def parse(self, text):
        try:
            return Time.parse(text)
        except ValueError:
            raise "Not match %r regular expresion"
        

class StrArg(SimpleArg):
    def __init__(self, regexp=None):
        self.regexp = regexp
        
    def parse(self, text):
        if self.regexp is None:
            return text
        elif re.match(self.regexp, text):
            return text
        else:
            raise "Not match %r regular expresion"

class EnumArg(SimpleArg):
    def __init__(self, values):
        self.values = values
        
    def parse(self, text):
        if text in self.values:
            try:
                return self.values[text]
            except:
                return text
        else: 
            raise "Not match %r regular expresion"

#####################################################################
# Arguments parser

def parse_arguments(arguments_table, text):
    args = text.split()
    for speclst in arguments_table:
        
        if speclst[1] == args[0]:
            try:
                result = [speclst[0]]
                argslst = args[1:]
                for spec in speclst[2:]:
                    val, argslst = spec.process(argslst)
                    result.append(val)
                
                return result
            except:
                pass
    
    raise 'Unknown arguments'

#####################################################################
# Arguments decorator

def args(*arglist):
    def wrapper_outer(func):
        def wrapper_inner(*args, **kwds):
            return func(*args, **kwds)
        
        arg_table = arglist[0]
        arg_table.append([wrapper_inner] + list(arglist[1:]))
        
        return wrapper_inner
    return wrapper_outer


if __name__ == '__main__':

    print cmd('goto -10%')
    print cmd('goto 1')
    print cmd('goto 10')
    print cmd('goto 1:24:45.678')
    print cmd('open ala_ma_kota.avi')
    
    print cmd('equa 6 -0.5')
    print cmd('equa all 0.6')
    print cmd('crop top 10%')
    print cmd('crop t 13%')



