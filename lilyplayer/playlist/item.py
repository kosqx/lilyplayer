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


import os.path

class PlaylistError(Exception):
    pass

class PlaylistItem(object):
    def __init__(self, filename, name=None, duration=None):
        if filename.startswith(('file://', 'dvd://')):
            self.filename = filename
        else:
            self.filename = os.path.abspath(filename)
        
        if name:
            self.name = name
        else:
            self.name = os.path.splitext(os.path.split(filename)[-1])[0]
            self.name = self.name.replace('.', ' ').replace('_', ' ').replace('  ', ' ')
        
        self.duration = duration

    def __repr__(self):
        return 'PlaylistItem(%r)' % self.filename

