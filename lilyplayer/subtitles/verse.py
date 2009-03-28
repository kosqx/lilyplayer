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


import unittest
    

from lilyplayer.utils.play_time import Time


class Verse(object):
    """ Single verse of subtitles """
    def __init__(self, start=None, stop=None, text=''):
        self.start = start
        self.stop = stop
        self.text = text

    def __repr__(self):
        if self.stop is None:
            return "Verse(Time('%r'), None, %r)" % (self.start, self.text)
        else:
            format = "Verse(Time('%r'), Time('%r'), %r)"
            return format % (self.start, self.stop, self.text)

    def __str__(self):
        return "%r -> %r = %r" % (self.start, self.stop, self.text)

    def __copy__(self):
        return Verse(self.start, self.stop, self.text)

    def __cmp__(self, other):
        return cmp([self.start, self.stop, self.text],
                [other.start, other.stop, other.text])

    @staticmethod
    def _process(time, mul, add):
        if time is None:
            return None
        else:
            return time * mul + add

    def process(self, mul, add):
        self.start = Verse._process(self.start, mul, add)
        self.stop = Verse._process(self.stop, mul, add)

    def processed(self, mul, add):
        return Verse(
            Verse._process(self.start, mul, add),
            Verse._process(self.stop, mul, add),
            self.text
        )


class VerseTestCase(unittest.TestCase):
    def testRepr(self):
        v0 = Verse(Time(s=10), None, 'Foo bar')
        s0 = repr(v0)
        r0 = eval(s0)
        
        v1 = Verse(Time(s=10), Time(s=15), 'Other bar')
        s1 = repr(v1)
        r1 = eval(s1)
        
        assert v0 == r0
        assert v1 == r1
        
    def testProcess(self):
        r0 = Verse(Time(s=13), Time(s=15), 'Foo bar')
        v0 = Verse(Time(s=10), Time(s=12), 'Foo bar')
        v0.process(1, Time(s=3))
        
        r1 = Verse(Time(s=16), Time(s=20), 'Foo bar')
        v1 = Verse(Time(s=8), Time(s=10), 'Foo bar')
        v1.process(2, Time())
        
        r2 = Verse(Time(s=13), Time(s=16), 'Foo bar')
        v2 = Verse(Time(s=10 * 16), Time(s=13 * 16), 'Foo bar')
        v2.process(1.0/16.0, Time(s=3))
        
        r3 = Verse(Time(s=27), None, 'Foo bar')
        v3 = Verse(Time(s=10), None, 'Foo bar')
        v3.process(3, Time(s=-3))
        
        assert v0 == r0
        assert v1 == r1
        assert v2 == r2
        assert v3 == r3

    def testProcessed(self):
        r0 = Verse(Time(s=27), None, 'Foo bar')
        v  = Verse(Time(s=10), None, 'Foo bar')
        v0 = v.processed(3, Time(s=-3))
        
        a = Verse(Time(s=27), None, 'Foo bar')
        b = a.processed(1, Time())
        
        assert v0 == r0
        assert id(a) != id(b), 'method processed should return new object'


if __name__ == '__main__':
    import copy
    import unittest
    unittest.main()
