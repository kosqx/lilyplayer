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
from copy import copy, deepcopy
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import logging


from lilyplayer.utils.play_time import Time, TimeRange
from lilyplayer.utils.utils import int_or, Null
from lilyplayer.subtitles.verse import Verse
from lilyplayer.subtitles.formats import Mpl2Format, MicroDvdFormat, TmPlayerFormat, SrtFormat


class SubtitlesLocator(object):
    def __init__(self, path, format='', encoding='utf-8'):
        self.path = path
        self.format = format, 
        self.encoding = encoding
    

class Subtitles(object):
    def __init__(self, raw=[], frame_based=False):
        self._frame_based = frame_based
        self._data = [copy(i) for i in raw]
        self._formats = {
            'mpl':       Mpl2Format,
            'srt':       SrtFormat,
            'tmp':       TmPlayerFormat,
            'mdvd':      MicroDvdFormat,
        }

        self._formats_names = {
            'mpl': 'mpl', 'mpl2': 'mpl',
            'srt': 'srt',
            'tmp': 'tmp', 'tmplayer':  'tmp',
            'mdvd': 'mdvd', 'microdvd': 'mdvd',
        }

    def __copy__(self):
        return Subtitles(list(self._data), self._frame_based)

    def __deepcopy__(self, memo):
        return Subtitles(deepcopy(self._data), self._frame_based)

    def __cmp__(self, other):
        return cmp((self._data,self._frame_based),
                (other._data, other._frame_based))

    def __add__(self, time):
        return deepcopy(self).process(1, time)

    def __sub__(self, time):
        return deepcopy(self).process(1, -time)

    def __mul__(self, factor):
        return deepcopy(self).process(factor, Time())

    def __div__(self, factor):
        return deepcopy(self).process(1.0 / factor, Time())

    def __nonzero__(self):
        return bool(self._data)

    def __str__(self):
        result = ["%s" % v for v in self._data]
        return "\n".join(result)

    def __repr__(self):
        result = ["%r" % v for v in self._data]
        result = ",\n".join(result)
        fb = str(self._frame_based)
        return ''.join(['Subtitles([\n', result, "\n], frame_based=", fb, ")"])

    # warning: experiment, dont use in final code!
    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __delitem__(self, key):
        del self._data[key]
        
        
    def _format_class(self, name):
        name = name.strip().lower()
        return self._formats[self._formats_names[name]]

    def load_string(self, data, format='', encoding='utf-8'):
        logging.debug('subtitles.load_string')
        def do_load(format, encoding):
            format_class = self._format_class(format)
            tmp, self._frame_based = format_class.load(data, encoding)
            self._data = [copy(i) for i in tmp]
            
        if not format:
            for format in self._formats:
                format_class = self._formats[format]
                print 'subtitles.load_string try: %r' % format
                try:
                    do_load(format, encoding)
                    logging.info("Opened subtitles file in format %r" % format)
                    return self
                except Exception, e:
                    #print '    fail', e
                    logging.exception('fail')
                    pass
        else:
            do_load(format, encoding)
            return self
    
    def load(self, afile, format='', encoding='utf-8'):
        #logging.info("Opening subtitles file in format %r" % afile)
        if isinstance(afile, basestring):
            stream = open(afile, 'r')
            opened = True
        else:
            stream = afile
            opened = False

        data = stream.read()
        self.load_string(data, format, encoding)

        if opened:
            stream.close()


    def save_string(self, format='srt', encoding='utf-8'):
        data = self._format_class(format).save(self._data, encoding)
        return data
    
    def save(self, afile, format='srt', encoding='utf-8'):
        if isinstance(afile, basestring):
            stream = open(afile, 'w')
            opened = True
        else:
            stream = afile
            opened = False

        stream.write(self.save_string(format, encoding))

        if opened:
            stream.close()

    def normalize(self):
        """ Make many normalizations on subtitles:
         - take care about lines which end time is before start
         - sort by time
        """
        return NotImplemented

    def split(self, times, use_positions=False):
        """ Split subtitle
            times - decite between:
             - lenght - lenght of files...
             - positions - positions where to cut
        """
        self.sort()
        size = len(times) + 1
        result = [Subtitles() for i in xrange(size)]
        #sums = [sum(times[:i], Time()) for i in xrange(1, size)]
        #sums.append(Time(h=1000000))

        if use_positions:
            pos = list(times)
            sums = list(times)
        else:
            sums = [sum(times[:i], Time()) for i in xrange(1, size)]#list(sums)
            pos = list(sums)

        pos.append(Time(h=1000000))

        index = 0
        for verse in self._data:
            while verse.start >= pos[index]:
                index += 1
            result[index].append(verse)

        for sub, shift in zip(result[1:], sums):
            sub.process(1, -shift)

        return result

    def join(self, subs):
        """ Join subtitle on specified times
            subs - list of
        """
        return NotImplemented
    
    def adjust_time(self, perchar=Time(), minimum=Time(s=2), decrease=False):
        for verse in self._data:
            #print verse
            #print perchar, len(verse.text)
            time = perchar * len(verse.text) + minimum + verse.start
            if verse.stop is None:
                verse.stop = time
            else:
                if decrease or verse.stop < time:
                    verse.stop = time
         
        return self
    
    def adjust_fps(self, fps):
        if self._frame_based:
            self.process(1.0 / fps, Time())
            self._frame_based = False
        return self

    def sort(self):
        self._data.sort()

        return self

    def process(self, mul, add):
        for record in self._data:
            record.process(mul, add)

        return self

    def at(self, time):
        """ Return list of texts what are specifiet for given time.
            Stop times for texts must be calculated.
        """
        result = []

        for i in self._data:
            if time in TimeRange(i.start, i.stop):
                result.append(i)

        return result

    def append(self, verse):
        assert isinstance(verse, Verse), ''
        self._data.append(verse)

    def extend(self, data):
        self._data.extend(data)

