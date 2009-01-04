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
import random


class PlaylistItem(object):
    def __init__(self, filename, name=None):
        self.filename = os.path.abspath(filename)
        if name:
            self.name = name
        else:
            self.name = os.path.split(filename)[-1]


class Playlist(object):
    def __init__(self, items):
        self.items = [PlaylistItem(i) for i in items]
        self.current = None
        self.mode = 'default'
    
    def get(self):
        if self.current is not None and 0 <= self.current < len(self.items):
            return self.items[self.current]
        else:
            return None

    def append(self, filename):
        self.items.append(PlaylistItem(filename))

    def append_and_goto(self, filename):
        self.items.append(PlaylistItem(filename))
        self.current = len(self.items) - 1
        return self.get()

    def goto(self, index):
        self.current = index
        return self.get()

    def next(self):
        if self.mode == 'repeat-one':
            if self.current is None:
                self.current = 0
        elif self.mode == 'repeat':
            if self.current is None:
                self.current = 0
            elif self.current >= (len(self.items) - 1):
                self.current = 0
            else:
                self.current += 1
        elif self.mode == 'shuffle':
            self.current = random.randint(len(self.items))
        else:
            if self.current is None:
                self.current = 0
            else:
                self.current += 1
        return self.get()

