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


import sys
import os
import os.path
import time
import random


from gui import Main


from play_time import Time
from player import Player
from arguments import PrefixArg, FloatArg, IntArg, TimeArg, StrArg, EnumArg, parse_arguments, args
from playlist import Playlist, PlaylistItem

import compose_thumbs

class Struct(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)
    
    def __repr__(self):
        args = ['%s=%r' % (i, self.__dict__[i]) for i in self.__dict__ if not i.startswith('_')]
        return 'Struct(' + ', '.join(args) + ')'

def prefix_value_change(prop, prefix, value):
    if prefix == '+':
        return prop + value
    elif prefix == '-':
        return prop - value
    else:
        return value


class Controler(object):
    arguments_table = []
        
    main_menu = [
        ('File', [
            'Open',
            'Close',
            None,
            'Exit',
            ]),
        ('View', [
            'Main Menu',
            'Controls',
            'Sidebar',
            'Playlist',
            'Logs',
            None,
            'Configuration',
            ]),
        ('Playback', [
            'Play',
            'Pause',
            'Stop',
            None,
            'Goto',
            None,
            ('Speed', [
                    '25%', '50%', '100%', '200%', '400%',
                ])
            ]),
        ('Video', [
            ('Track', [
                'Off',
                None,
                ]),
            ('Aspect ratio', [
                'Fill', 'Default', None,
                '5:4', '4:3', '16:10', '16:9',
                ]),
            ]),
        ('Audio', [
            ('Track', [
                'Off',
                None,
                ]),
            ('Balance', [
                'Central', None,
                'Move left', 'Move right',
                ]),
            None,
            'Mute',
            'Volume Down',
            'Volume Up',
            
            ]),
        ('Tools', [
            'Snapshot',
            'Thumbinals',
            None,
            'Subtitle download',
            ]),
        ('Help', [
            'Help',
            None,
            'About',
            ]),
    ]
        
    def __init__(self):
        pass
        #self.player = Player.create('gstreamer', self, self.movie_window.winId())
        self.gui = Main(self)
        self.player = Player.create('gstreamer', self.gui, self.gui.movie_window.winId())
    
    def exec_(self):
        self.gui.exec_()
    
    def dispatch(self, args):
        parsed = parse_arguments(self.arguments_table, args)
        parsed[0](*([self] + parsed[1:]))


    def keyboard_shortcut(self, keys):
        keys_map = {
            'Space': 'toggle',
            
            'Up'       : 'volume +10%',
            'Down'     : 'volume -10%',
            'WheelUp'  : 'volume +5%',
            'WheelDown': 'volume -5%',
            'M'        : 'mute',
            
            'F'    : 'fullscreen',
            'F11'  : 'fullscreen',
            
            'Left'        : 'goto -0:00:30',
            'Right'       : 'goto +0:00:30',
            'Alt+Left'    : 'goto -0:00:05',
            'Alt+Right'   : 'goto +0:00:05',
            'Shift+Left'  : 'goto -0:02:00',
            'Shift+Right' : 'goto +0:02:00',
            
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
        
        if keys in keys_map:
            msg = keys_map[keys]
            self.dispatch(msg)

    def on_start(self):
        self.playlist = Playlist(sys.argv[1:])
        
        self.open_item(self.playlist.next())
        self.gui.update_menu(self.main_menu)

    def on_timer(self):
        if self.player.state == 'finish':
            next = self.playlist.next()
            self.open_item(next)
        #self.slider.setValue(int(self.player.position_fraction * 1000))
        self.gui.controls._redraw(self)

    def open_item(self, item):
        if item:
            self.player.stop()
            self.gui.window.setWindowTitle("%s Lily Player:"  % item.name)
            self.player.open(item.filename)
            self.player.play()
        else:
            self.gui.window.setWindowTitle("Lily Player")
            self.player.stop()

    def get_fullscreen(self):
        return self.gui.do_get_fullscreen()
    
    def set_fullscreen(self, value=None):
        if value is None:
            value = not self.gui.do_get_fullscreen()
        
        self.gui.do_set_fullscreen(value)



    @args(arguments_table, 'exit')
    def cmd_exit(self):
        # TODO: make this better
        exit()

    @args(arguments_table, 'open', StrArg())
    def cmd_open(self, url):
        self.player.open(url)
        
    @args(arguments_table, 'opendlg')
    def cmd_opendlg(self):
        filename = QFileDialog.getOpenFileName(self.window, 'Open file', '/home/kosqx')
        print filename
        if filename:
            self.player.open(str(filename))
    
    @args(arguments_table, 'close')
    def cmd_close(self):
        self.player.close()
    

    @args(arguments_table, 'speed', PrefixArg(['+', '-', '=', '']), FloatArg(0.25, 4.0))
    def cmd_speed(self, prefix, value):
        self.player.speed = prefix_value_change(self.player.speed, prefix, value)
        
    @args(arguments_table, 'goto', PrefixArg(['+', '-', '=', '']), FloatArg(0.0, 1.0))
    def cmd_goto_pos(self, prefix, value):
        self.player.position_fraction = prefix_value_change(self.player.position_fraction, prefix, value)
    
    @args(arguments_table, 'goto', PrefixArg(['+', '-', '=', '']), TimeArg())
    def cmd_goto_time(self, prefix, value):
        self.player.position = prefix_value_change(self.player.position, prefix, value)
    
    @args(arguments_table, 'volume', PrefixArg(['+', '-', '=', '']), FloatArg(0.0, 1.0))
    def cmd_volume(self, prefix, value):
        self.player.volume = prefix_value_change(self.player.volume, prefix, value)
        
    @args(arguments_table, 'mute')
    def cmd_mute(self):
        self.player.mute = None
    
    @args(arguments_table, 'snap')
    def cmd_snap(self):
        format, data = self.player.snapshot()
        filename = os.path.expanduser('~/lily_%s.%s' % (time.strftime('%Y-%m-%d_%H:%M:%S'), format))
        fo = open(filename, 'wb')
        fo.write(data)
        fo.close()

    @args(arguments_table, 'thumb', IntArg(1, 1000))
    def cmd_snap(self, count):
        saved_pos = self.player.position_fraction
        saved_state = self.player.state
        self.player.pause()
        
        result = []
        
        for i in xrange(1, count + 1):
            last_pos = self.player.position_fraction
            seek_pos = i * (1.0 / (count + 1))
            self.player.position_fraction = seek_pos

            format, data = self.player.snapshot()
            label = str(self.player.position)
            result.append((data, label))

            #filename = os.path.expanduser('~/thumb_%.4d.%s' % (i, format))
            #fo = open(filename, 'wb')
            #fo.write(data)
            #fo.close()

        compose_thumbs.compose(
                result, 
                outfile=os.path.join(os.path.expanduser('~'), 'thumb.png'),
                size=200, cols=4, border=5,
        )
        
        self.player.position_fraction = saved_pos
        self.player.state = saved_state

    @args(arguments_table, 'play')
    def cmd_play(self):
        self.player.play()
    
    @args(arguments_table, 'pause')
    def cmd_pause(self):
        self.player.pause()
    
    @args(arguments_table, 'stop')
    def cmd_stop(self):
        self.player.stop()
        
    @args(arguments_table, 'toggle')
    def cmd_toggle(self):
        self.player.toggle()
        
    @args(arguments_table, 'fullscreen')
    def cmd_fullscreen(self):
        self.set_fullscreen(None)
        
        
    @args(arguments_table, 'playlist-next')
    def cmd_playlist_next(self):
        print 'playlist next'
        self.open_item(self.playlist.next())
        
    @args(arguments_table, 'playlist-mode', EnumArg(['repeat-one', 'repeat', 'shuffle', 'default']))
    def cmd_playlist_mode(self, mode):
        self.playlist.mode = mode
        
    @args(arguments_table, 'playlist-goto', IntArg(0))
    def cmd_playlist_goto(self, index):
        self.open_item(self.playlist.goto(index))

if __name__ == '__main__':
    controler = Controler() 
    controler.exec_()
