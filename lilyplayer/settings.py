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
        
        'Tab':       'view-sidebar toggle',
        'Backspace': 'view-sidebar toggle',
        
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
        
        
        'Alt+1': 'video-scale  25%',
        'Alt+2': 'video-scale  50%',
        'Alt+3': 'video-scale  75%',
        'Alt+4': 'video-scale 100%',
        'Alt+5': 'video-scale 125%',
        'Alt+6': 'video-scale 150%',
        'Alt+7': 'video-scale 175%',
        'Alt+8': 'video-scale 200%',
        'Alt+9': 'video-scale 225%',
        'Alt+0': 'video-scale 250%',
        
        'Ctrl+1': 'video-scale  50%',
        'Ctrl+2': 'video-scale 100%',
        'Ctrl+3': 'video-scale 150%',
        'Ctrl+4': 'video-scale 200%',
        'Ctrl+5': 'video-scale 250%',
        'Ctrl+6': 'video-scale 300%',
        'Ctrl+7': 'video-scale 350%',
        'Ctrl+8': 'video-scale 400%',
        'Ctrl+9': 'video-scale 450%',
        'Ctrl+0': 'video-scale 500%',
        
        
    },
    'gui': {
        'theme': 'black',
        'thumb': {
            'cols':   4,
            'rows':   8,
            'size':   200,
            'margin': 10,
        },
    },
}

def get(name):
    parts = name.split('.')
    tmp = _settings_data

    for i in parts:
        tmp = tmp[i]
        
    return tmp

def set(name, value):
    parts = name.split('.')
    tmp = _settings_data

    for i in parts[:-1]:
        if i not in tmp:
            tmp[i] = {}
        tmp = tmp[i]
    
    tmp[parts[-1]] = value   

def get_path(space, *names, **conf):
    if space == '~':
        parts = [os.path.expanduser('~'), '.lilyplayer']
    else:
        parts = ['/usr/share/lilyplayer', space]

    parts.extend(names)
    
    if conf.get('mkdir', False):
        dir = os.path.join(parts[:-1])
        if not os.path.exists(dir):
            os.makedirs(dir)
    
    path = os.path.join(*parts)
    return path
    
    

