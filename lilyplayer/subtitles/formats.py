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


class SrtFormat(SubtitlesFormat):
    """ Support for SRT subtitle file format

    """
    
    name       = 'srt'
    label      = 'SubRip subtitles'
    extensions = ['srt']
    mimes      = ['application/x-subrip']

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


#class SamiFormat(SubtitlesFormat):
#    name       = 'sami'
#    label      = 'Synchronized Accessible Media Interchange'
#    extensions = ['smi', 'sami']
#    mimes      = ['application/x-sami']
#
#    @staticmethod
#    def load(data, encoding=None):
#        """ Load subtitle """
#
#        result = []
#        return result, False
#
#    @staticmethod
#    def save(data, encoding=None):
#        result = []
#        return '\n'.join(result)
