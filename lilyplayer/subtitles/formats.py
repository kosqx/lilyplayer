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

import re
#from copy import copy, deepcopy
import unittest

#try:
    #from cStringIO import StringIO
#except ImportError:
    #from StringIO import StringIO

from lilyplayer.utils.play_time import Time, TimeRange 
from lilyplayer.utils.utils import int_or
from verse import Verse



class SubtitlesFormat(object):
    pass


class SubtitlesFormatError(Exception):
    pass


def to_unicode(text, encoding):
    if encoding is None:
        return unicode(text)
    else:
        return unicode(text, encoding)


def from_unicode(text, encoding):
    if encoding is None:
        return text.encode()
    else:
        return text.encode(encoding)


class Mpl2Format(SubtitlesFormat):
    """ Support for MPL2 subtitle file format

    """
    #frame_based = False

    @staticmethod
    def load(data, encoding=None):
        """ Load subtitle """

        pattern = re.compile(r"\[(?P<start>\d+)\]\[(?P<stop>\d*)\](?P<text>.*)")
        result = []
        lines = data.splitlines()

        for line in lines:
            m = pattern.match(to_unicode(line, encoding))
            g = m.groupdict()

            start = Time.from_seconds(int(g['start']), 1)
            try:
                stop = Time.from_seconds(int(g['stop']), 1)
            except ValueError:
                stop = None
            text = g['text'].replace('|', '\n')

            result.append(Verse(start, stop, text))

        return result, False

    @staticmethod
    def save(data, encoding=None):
        #print 'Saving'
        #raise KeyError
        result = []

        for record in data:
            text = from_unicode(record.text.replace('\n', '|'), encoding)
            #text = text.replace('', '')
            if record.stop is None:
                result.append("[%d][]%s" % (record.start.to_seconds(1), text))
            else:
                result.append("[%d][%d]%s" % (record.start.to_seconds(1),
                        record.stop.to_seconds(1), text))
        return '\n'.join(result)


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



class MicroDvdFormat(SubtitlesFormat):
    """ Support for MicroDVD subtitle file format

    """

    #frame_based = True

    @staticmethod
    def load(data, encoding=None):
        """ Load subtitle """
        
        pattern = re.compile(r"\{(?P<start>\d+)\}\{(?P<stop>\d*)\}(?P<text>.*)")
        result = []
        lines = data.splitlines()

        for line in lines:
            m = pattern.match(to_unicode(line, encoding))
            d = m.groupdict()
            print d
            start = Time.from_seconds(int(d['start']))
            try:
                stop = Time.from_seconds(int(d['stop']))
            except:
                stop = None
            text = d['text'].replace('|', '\n')

            result.append(Verse(start, stop, text))

        return result, True

    @staticmethod
    def save(data, encoding=None):
        result = []

        for record in data:
            text = from_unicode(record.text.replace('\n', '|'), encoding)
            if record.stop is None:
                result.append("{%d}{}%s" % (record.start.to_seconds(), text))
            else:
                result.append("{%d}{%d}%s" % (record.start.to_seconds(),
                        record.stop.to_seconds(), text))
        return '\n'.join(result)


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


class TmPlayerFormat(SubtitlesFormat):
    """ Support for TM Player subtitle file format

    """

    #frame_based = False

    @staticmethod
    def load(data, encoding=None):
        """ Load subtitle """


        pattern = r"(?P<h>\d*):(?P<m>\d*):(?P<s>\d*)[:,= ](?P<text>.*)"
        pattern = re.compile(pattern)
        result = []
        lines = data.splitlines()

        for line in lines:
            m = pattern.match(to_unicode(line, encoding))
            d = m.groupdict()

            h = int_or(d['h'], 0)
            m = int_or(d['m'], 0)
            s = int_or(d['s'], 0)
            text = d['text'].replace('|', '\n')
            start = Time(h=h, m=m, s=s)

            result.append(Verse(start, None, text))
            #print Verse(start, None, text)

        return result, False

    @staticmethod
    def save(data, encoding=None):
        result = []

        for record in data:
            text = from_unicode(record.text.replace('\n', '|'), encoding)
            result.append("%s:%s" % (record.start, text))
        return '\n'.join(result)


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


class SrtFormat(SubtitlesFormat):
    """ Support for SRT subtitle file format

    """

    frame_based = False

    @staticmethod
    def load(data, encoding=None):
        """ Load subtitle """

        result = []
        lines = data.splitlines()

        pattern = r"(?P<start>\d+:\d+:\d+,\d*) --> (?P<stop>\d+:\d+:\d+,\d*)"
        pattern = re.compile(pattern)

        state, text = 0, []
        for line in lines:
            line = to_unicode(line, encoding)
            if state == 0:
                state = 1

            elif state == 1:
                m = pattern.match(line)
                d = m.groupdict()
                start = Time.parse(d['start'])
                stop = Time.parse(d['stop'])
                state = 2

            elif state == 2:
                if line.strip() == "":
                    result.append(Verse(start, stop, '\n'.join(text)))
                    text = []
                    state = 0
                else:
                    text.append(line.strip())

        return result, False


    @staticmethod
    def save(data, encoding=None):
        result = []

        for index, record in enumerate(data):
            text = from_unicode(record.text, encoding)
            
            result.append("%d" % (index + 1))
            result.append("%r --> %r" % (record.start, record.stop))
            result.append("%s" % text)
            result.append("")

        return '\n'.join(result)


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
