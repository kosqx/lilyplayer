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
import logging


from lilyplayer.playlist.item import PlaylistItem
import lilyplayer.playlist.formats as formats
import lilyplayer.utils.utils as utils


class Playlist(object):
    def __init__(self, items):
        self.formats = {}
        for i in dir(formats):
            obj = getattr(formats, i)
            if obj.__class__.__name__ == 'type' and formats.PlaylistFormat in obj.mro()[1:]:
                self.formats[obj.extension] = obj
        
        self.items = []
        for item in items:
            self.append(item)
        self.current = None
        self.mode = 'default'
    
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, key):
        return self.items[key]
    
    def __setitem__(self, key, value):
        self.items[key] = value
    
    def __delitem__(self, key):
        if key > self.current:
            self.current -= 1
        del self.items[key]

    
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
        
    def sort(self, method):
        methods = {
            'random':   lambda i, o: random.random(),
            'filename': lambda i, o: o.filename,
            'name':     lambda i, o: o.name,
            'reverse':  lambda i, o: -i,
        }
        if method not in methods:
            return
        
        # standard Decorate-Sort-Undecorate
        tmp = []
        
        for index, object in enumerate(self.items):
            tmp.append((methods[method](index, object), index, object))
        
        tmp.sort()
        
        self.items = []
        current = self.current
        for new_index, (skip, index, object) in enumerate(tmp):
            self.items.append(object)
            if current == index:
                self.current = new_index
    
    def playlist_formats(self):
        return [("%s File" % i.upper(), [i]) for i in self.formats]
        
    def media_formats(self):
        formats = [
            ['avi'],
            ['mp3'],
        ]
                
    def save(self, filename, format):
        try:
            obj = self.formats[format]
        except KeyError:
            logging.warning('Format %r not supported' % format)
            return None
        
        dump = obj.dumps(self.items)
        utils.File(filename).write(dump)
        

