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
    Usefull time position class
"""

import re


from utils import int_or

class Time(object):
    def __init__(self, value=None, h=0, m=0, s=0, ms=0, raw=0):
        if value is None:
            tmp = h * 3600 * 1000 + m * 60 * 1000 + s * 1000 + ms + raw
            self.time = int(tmp)
        elif isinstance(value, basestring):
            self.time = Time.parse(value).time
        elif isinstance(value, Time):
            self.time = value.time
        elif isinstance(value, int) or isinstance(value, long)\
                or isinstance(value, float):
            self.time = int(value * 1000)


    def __repr__(self):
        if self.time >= 0:
            prefix, v = '', self.time
        else:
            prefix, v = '-', -self.time
        return "%s%.2d:%.2d:%.2d,%.3d" % (
                (prefix),
                (v / 3600 / 1000),
                (v / 60 / 1000 % 60),
                (v / 1000 % 60),
                (v % 1000)
            )

    def __str__(self):
        if self.time >= 0:
            prefix, v = '', self.time
        else:
            prefix, v = '-', -self.time
        return "%s%.2d:%.2d:%.2d" % (
                (prefix),
                (v / 3600 / 1000),
                (v / 60 / 1000 % 60),
                (v / 1000 % 60)
            )

    def __cmp__(self, other):
        if other is None:
            return -1
        else:
            return cmp(self.time, other.time)

    def __add__(self, other):
        return Time(raw=self.time + other.time)

    def __sub__(self, other):
        return Time(raw=self.time - other.time)

    def __neg__(self):
        return Time(raw=-self.time)

    def __mul__(self, other):
        return Time(raw=self.time * other)

    def __div__(self, other):
        if isinstance(other, Time):
            return float(self.time) / float(other.time)
        else:
            return Time(raw=self.time / other)

    def __nonzero__(self):
        return self.time != 0

    def format(self, spec):
        """ """
        
        def do_format(spec, time):
            if spec == '%%':
                return '%'

            value = 0

            prec = spec[1:-1]
            if prec == '':
                prec = 0
            else:
                prec = int(prec)

            what = spec[-1:]

            if what == 'h':
                value = time.hours()
            elif what == 'H':
                value = time.total_hours()

            elif what == 'm':
                value = time.minutes()
            elif what == 'M':
                value = time.total_minutes()

            elif what == 's':
                value = time.seconds()
            elif what == 'S':
                value = time.total_seconds()
            
           
            
            if value == 0 and prec == 0:
                return ''
            
            value = str(value)
            
            return '0' * (prec - len(value)) + value
            
        parts = re.split(r'(%%|%\d?[hHmMsSfF])', spec)
        parts[1::2] = [do_format(i, self) for i in parts[1::2]]
        
        return ''.join(parts)


    def total_miliseconds(self):
        """ """
        return self.time

    def miliseconds(self):
        """ """
        return self.time % 1000

    def total_seconds(self):
        """ """
        return self.time / 1000

    def seconds(self):
        """ """
        return self.time / 1000 % 60

    def total_minutes(self):
        """ """
        return self.time / (1000 * 60)

    def minutes(self):
        """ """
        return self.time / (1000 * 60) % 60

    def total_hours(self):
        """ """
        return self.time / (1000 * 60 * 60)

    def hours(self):
        """ """
        return self.time / (1000 * 60 * 60) % 24

    def days(self):
        """ """
        return self.time / (1000 * 60 * 60 * 24)

    def to_seconds(self, prec = 0):
        """ Get seconds number from object. The prec argument show exponent 
            of number seconds.
            Examples:
             - Time(s=1000).to_seconds()   -> 1000
             - Time(s=1000).to_seconds(3)  -> 1000000
             - Time(s=1000).to_seconds(-3) -> 1
        """
        ex = prec - 3
        if ex >= 0:
            time = self.time * 2 * 10 ** ex
        else:
            time = self.time * 2 / 10 ** (-ex)
        # round not truncate
        return (time + 1) / 2


    @staticmethod
    def parse(text):
        try:
            pattern = r"^\s*(?P<sign>[-\+]?)(((?P<h>\d*):)?(?P<m>\d*):)?(?P<s>\d*)([,\.](?P<ms>\d*))?\s*$"
            pattern = re.compile(pattern)
            match = pattern.match(text)
            groups = match.groupdict()
            
            h = int_or(groups['h'], 0)
            m = int_or(groups['m'], 0)
            s = int_or(groups['s'], 0)
            ms = int_or(("%s%s" % (groups['ms'], '000'))[:3], 0)
            return Time(h=h, m=m, s=s, ms=ms)
        except:
            raise ValueError, "Can not parse text"

    @staticmethod
    def from_seconds(sec, prec = 0):
        """ Create Time object from number. Second argument show exponent 
            of number seconds.
            Equal examples:
             - from_seconds(1000, 0)
             - from_seconds(1000000, 3)
             - from_seconds(1, -3)
        """
        ex = 3 - prec
        if ex >= 0:
            return Time(raw=sec * 10 ** ex)
        else:
            return Time(raw=sec / 10 ** (-ex))







class TimeRange(object):
    """ Obustronnie domkniety przedzial czasowy

    """
    def __init__(self, start = None, stop = None):
        self.start = start
        self.stop = stop

    def __contains__(self, other):
        return self.start <= other and other <= self.stop

    def __str__(self):
        return "[%s, %s]" % (self.start, self.stop)
    
    def __repr__(self):
        return "[%r, %r]" % (self.start, self.stop)
    
    def lenght(self):
        return self.stop - self.start



