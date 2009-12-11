#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest


from lilyplayer.utils.play_time import Time
from lilyplayer.subtitles.verse import Verse
from lilyplayer.subtitles.formats import Mpl2Format, MicroDvdFormat, TmPlayerFormat, SrtFormat


class Mpl2FormatTestCase(unittest.TestCase):
    def setUp(self):
        self.tests = [
            ("[0][]", [Verse(Time(), None, u"")]),
            ("[0][1]", [Verse(Time(), Time(ms=100), u"")]),
            ("[1234][]asdf", [Verse(Time(ms=123400), None, u"asdf")]),
            ("[1234][7654]asdf", [Verse(Time(ms=123400), Time(ms=765400), u"asdf")]),
        ]
    
    def testLoad(self):
        for test in self.tests:
            self.assertEquals(Mpl2Format.load(test[0]), (test[1], False))
    
    def testSave(self):
        for test in self.tests:
            self.assertEquals(Mpl2Format.save(test[1]), test[0])
    
    #def testMisc(self):
        #self.assertEquals(Mpl2Format.frame_based, False)


class MicroDvdFormatTestCase(unittest.TestCase):
    def setUp(self):
        self.tests = [
            ("{0}{}", [Verse(Time(), None, u"")]),
            ("{0}{1}", [Verse(Time(), Time(s=1), u"")]),
            ("{1234}{}asdf", [Verse(Time(s=1234), None, u"asdf")]),
            ("{1234}{7654}asdf", [Verse(Time(s=1234), Time(s=7654), u"asdf")]),
        ]
    
    def testLoad(self):
        for test in self.tests:
            self.assertEquals(MicroDvdFormat.load(test[0]), (test[1], True))
    
    def testSave(self):
        for test in self.tests:
            self.assertEquals(MicroDvdFormat.save(test[1]), test[0])
    
    #def testMisc(self):
        #self.assertEquals(MicroDvdFormat.frame_based, True)


class TmPlayerFormatTestCase(unittest.TestCase):
    def setUp(self):
        self.tests = [
            ("00:00:00:", [Verse(Time(), None, u"")]),
            ("01:02:03:", [Verse(Time(h=1, m=2, s=3), None, u"")]),
            ("01:02:03:asdf", [Verse(Time(h=1, m=2, s=3), None, u"asdf")]),
            ("01:02:03:asdf", [Verse(Time(h=1, m=2, s=3), None, u"asdf")]),
        ]
    
    def testLoad(self):
        for test in self.tests:
            self.assertEquals(TmPlayerFormat.load(test[0]), (test[1], False))
    
    def testSave(self):
        for test in self.tests:
            self.assertEquals(TmPlayerFormat.save(test[1]), test[0])
    
    #def testMisc(self):
        #self.assertEquals(TmPlayerFormat.frame_based, False)


class SrtFormatTestCase(unittest.TestCase):
    def setUp(self):
        self.tests = [
            ("1\n00:00:00,000 --> 00:00:01,234\n\n",
                    [Verse(Time(), Time(s=1, ms=234), u"")]),
            #("01:02:03:", [(Time(h=1, m=2, s=3), None, "")]),
            #("01:02:03:asdf", [(Time(h=1, m=2, s=3), None, "asdf")]),
            #("01:02:03:asdf", [(Time(h=1, m=2, s=3), None, "asdf")]),
        ]
    
    def testLoad(self):
        for test in self.tests:
            self.assertEquals(SrtFormat.load(test[0]), (test[1], False))
    
    def testSave(self):
        for test in self.tests:
            self.assertEquals(SrtFormat.save(test[1]), test[0])
    
    #def testMisc(self):
        #self.assertEquals(SrtFormat.frame_based, False)


if __name__ == '__main__':
    unittest.main()
