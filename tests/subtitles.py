#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


from lilyplayer.utils.play_time import Time
from lilyplayer.subtitles.verse import Verse
from lilyplayer.subtitles.subtitles import Subtitles


class SubtitlesTestCase(unittest.TestCase):
    def setUp(self):
        self.data = [
            Verse(Time(s=0), Time(s=1), "movie"),
            Verse(Time(s=1), Time(s=2), "foo"),
            Verse(Time(s=2), Time(s=3), "bar"),
            Verse(Time(s=3), Time(s=4), "..."),
        ]

        self.mpl = "[0][10]movie\n" "[10][20]foo\n" \
                "[20][30]bar\n" "[30][40]...\n"


    #def testSplit(self):
        #sub = Subtitles(raw=self.data)

        #test0 = [
            #Subtitles(raw=[
                #Verse(Time(s=0), Time(s=1), "movie"),
                #Verse(Time(s=1), Time(s=2), "foo"),
                #Verse(Time(s=2), Time(s=3), "bar"),
                #Verse(Time(s=3), Time(s=4), "..."),
            #])
        #]

        #test1 = [
            #Subtitles(raw=[
                #Verse(Time(s=0), Time(s=1), "movie"),
                #Verse(Time(s=1), Time(s=2), "foo"),
            #]),
            #Subtitles(raw=[
                #Verse(Time(s=0.5), Time(s=1.5), "bar"),
                #Verse(Time(s=1.5), Time(s=2.5), "..."),
            #])
        #]

        #test2 = [
            #Subtitles(raw=[
                #Verse(Time(s=0), Time(s=1), "movie"),
                #Verse(Time(s=1), Time(s=2), "foo"),
            #]),
            #Subtitles(raw=[
                #Verse(Time(s=0.5), Time(s=1.5), "bar"),
            #]),
            #Subtitles(raw=[
                #Verse(Time(s=0.5), Time(s=1.5), "..."),
            #])
        #]

        #data0 = sub.split([])
        #data1 = sub.split([Time(s=1.5)])
        #data2a = sub.split([Time(s=1.5), Time(s=2.5)], use_positions=True)
        #data2b = sub.split([Time(s=1.5), Time(s=1.0)])

        #self.assertEquals(len(data0), 1)
        #self.assertEquals(len(data1), 2)
        #self.assertEquals(len(data2a), 3)
        #self.assertEquals(len(data2b), 3)

        #self.assertEquals(data2a, data2b)

        #self.assertEquals(data0, test0)
        #self.assertEquals(data1, test1)
        #self.assertEquals(data2a, test2)
        #self.assertEquals(data2b, test2)


    def testLoadMpl2(self):
        sub = Subtitles()
        sub.load(StringIO(self.mpl), 'mpl2', 'utf-8')
        self.assertEquals(sub, Subtitles(raw=self.data))

    def testAt(self):
        sub = Subtitles(raw=self.data)
        self.assertEquals(sub.at(Time()), [Verse(Time(s=0), Time(s=1), "movie")])
        self.assertEquals(sub.at(Time(s=1)), [Verse(Time(s=0), Time(s=1), "movie"),
                Verse(Time(s=1), Time(s=2), "foo")])
        self.assertEquals(sub.at(Time(ms=2300)), [Verse(Time(s=2), Time(s=3), "bar")])
        self.assertEquals(sub.at(Time(s=9)), [])


    def testLoadDetect(self):
        pass
        #sub = Subtitles()
        #sub.load('../tests/sub/elephants_dream.srt')
        #print sub
        #print sub.save_string('mpl2')

    def testSave(self):
        pass

if __name__ == '__main__':
    unittest.main()

