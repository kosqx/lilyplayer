#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest


from lilyplayer.utils.play_time import Time
from lilyplayer.subtitles.verse import Verse


class VerseTestCase(unittest.TestCase):
    def testRepr(self):
        v0 = Verse(Time(s=10), None, 'Foo bar')
        s0 = repr(v0)
        r0 = eval(s0)
        
        v1 = Verse(Time(s=10), Time(s=15), 'Other bar')
        s1 = repr(v1)
        r1 = eval(s1)
        
        self.assertEquals(v0, r0)
        self.assertEquals(v1, r1)
        
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
        
        self.assertEquals(v0, r0)
        self.assertEquals(v1, r1)
        self.assertEquals(v2, r2)
        self.assertEquals(v3, r3)

    def testProcessed(self):
        r0 = Verse(Time(s=27), None, 'Foo bar')
        v  = Verse(Time(s=10), None, 'Foo bar')
        v0 = v.processed(3, Time(s=-3))
        
        a = Verse(Time(s=27), None, 'Foo bar')
        b = a.processed(1, Time())
        
        self.assertEquals(v0, r0)
        self.assertNotEquals(id(a), id(b), 'method processed should return new object')


if __name__ == '__main__':
    unittest.main()

