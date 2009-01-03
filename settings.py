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

_settings_data = {
    'shortcut': {
        'Space': 'toggle',
        
        'Up':        'volume +10%',
        'Down':      'volume -10%',
        'WheelUp':   'volume +5%',
        'WheelDown': 'volume -5%',
        'M':         'mute',
        
        'F':     'fullscreen',
        'F11':   'fullscreen',
        'Esc':   'fullscreen off',
        
        'Q':      'cmddlg',
        'Grave':  'cmddlg',
        
        'Left':         'goto -0:00:30',
        'Right':        'goto +0:00:30',
        'Alt+Left':     'goto -0:00:05',
        'Alt+Right':    'goto +0:00:05',
        'Shift+Left':   'goto -0:02:00',
        'Shift+Right':  'goto +0:02:00',
        
        '0': 'goto  0%',
        '1': 'goto 10%',
        '2': 'goto 20%',
        '3': 'goto 30%',
        '4': 'goto 40%',
        '5': 'goto 50%',
        '6': 'goto 60%',
        '7': 'goto 70%',
        '8': 'goto 80%',
        '9': 'goto 90%',
    }
}

def get(name):
    return _settings_data[name]

def set(name, value):
    _settings_data[name] = value

def get_path(space, name):
    return os.path.join(os.path.dirname(__file__), space, name)

