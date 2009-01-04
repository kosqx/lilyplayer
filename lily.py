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
import platform


from gui import Main


from play_time import Time
from player import Player
from arguments import PrefixArg, FloatArg, IntArg, TimeArg, StrArg, EnumArg, parse_arguments, args
from playlist import Playlist, PlaylistItem

import compose_thumbs
import settings
import utils

__version__ = (0, 3, 1)
__author__ = 'Krzysztof Kosyl'
_copyright__ = 'GNU General Public License'


def prefix_value_change(prop, prefix, value):
    if prefix == '+':
        return prop + value
    elif prefix == '-':
        return prop - value
    else:
        return value

class MenuItem(object):
    @staticmethod
    def text_to_name(text):
        result = []
        for c in text.lower():
            if ('a' <= c <= 'z') or ('0' <= c <= '9'):
                result.append(c)
        return ''.join(result)
    
    def __init__(self, text, name=None, cmd=None, submenu=None):
        self.text = text
        if name:
            self.name = name
        else:
            self.name = MenuItem.text_to_name(text)
        
        self.cmd     = cmd
        self.submenu = submenu
        
    def is_item(self):
        return self.cmd is not None
    
    def is_submenu(self):
        return self.submenu is not None
    
    def is_separator(self):
         return (self.cmd is None) and (self.submenu is None)
    
    def by_name(self, name):
        result = []
        
        if self.submenu:
            for item in self.submenu:
                if name == item.name or (name.endswith(':') and item.name.startswith(name)):
                    result.append(item)
        
        return result

class Controler(object):
    arguments_table = []
        
    #main_menu = [
        #('File', [
            #'Open',
            #'Close',
            #None,
            #'Exit',
            #]),
        #('View', [
            #'Main Menu',
            #'Controls',
            #'Sidebar',
            #'Playlist',
            #'Logs',
            #None,
            #'Configuration',
            #]),
        #('Playback', [
            #'Play',
            #'Pause',
            #'Stop',
            #None,
            #'Goto',
            #None,
            #('Speed', [
                    #'25%', '50%', '100%', '200%', '400%',
                #])
            #]),
        #('Video', [
            #('Track', [
                #'Off',
                #None,
                #]),
            #('Aspect ratio', [
                #'Fill', 'Default', None,
                #'5:4', '4:3', '16:10', '16:9',
                #]),
            #]),
        #('Audio', [
            #('Track', [
                #'Off',
                #None,
                #]),
            #('Balance', [
                #'Central', None,
                #'Move left', 'Move right',
                #]),
            #None,
            #'Mute',
            #'Volume Down',
            #'Volume Up',
            
            #]),
        #('Tools', [
            #'Snapshot',
            #'Thumbinals',
            #None,
            #'Subtitle download',
            #]),
        #('Help', [
            #'Help',
            #None,
            #'About',
            #]),
    #]
    
    main_menu = MenuItem('', submenu=[
        MenuItem('File', submenu=[
            MenuItem('Open', cmd='opendlg'),
            MenuItem('Close', cmd='close'),
            MenuItem(''),
            MenuItem('Exit', cmd='exit'),
        ]),
        MenuItem('Playback', submenu=[
            MenuItem('Play', cmd='play'),
            MenuItem('Pause', cmd='pause'),
            MenuItem('Stop', cmd='stop'),
            MenuItem(''),
            MenuItem('Goto', cmd='gotodlg'),
            MenuItem(''),
            MenuItem('Speed', submenu=[
                MenuItem('25%',  cmd='speed 25%'),
                MenuItem('50%',  cmd='speed 50%'),
                MenuItem('100%', cmd='speed 100%'),
                MenuItem('200%', cmd='speed 25%'),
                MenuItem('400%', cmd='speed 25%'),
            ]),
        ]),
        MenuItem('Tools', submenu=[
            MenuItem('Snapshot', cmd='snap'),
            MenuItem('Thumbinals', cmd='thumbdlg'),
        ]),
        MenuItem('Help', submenu=[
            MenuItem('About', cmd='about'),
        ]),
    ])

    def __init__(self):
        pass
        #self.player = Player.create('gstreamer', self, self.movie_window.winId())
        self.gui = Main(self)
        self.player = Player.create('gstreamer', self.gui, self.gui.movie_window.winId())
        settings.get_path('data', 'mainicon.png')
    
    def exec_(self):
        self.gui.exec_()
    
    def dispatch(self, args):
        if args is not None:
            parsed = parse_arguments(self.arguments_table, args)
            parsed[0](*([self] + parsed[1:]))


    def keyboard_shortcut(self, keys):
        shortcuts = settings.get('shortcut')
        if keys in shortcuts:
            msg = shortcuts[keys]
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



    def open_dlg(self):
        filename = self.gui.do_file_dialog('Open file', mode='open', path=None, filter=None)
        print filename
        if filename:
            self.open(filename)

    def open(self, filename):
        item = self.playlist.append_and_goto(filename)
        self.open_item(item)

    def open_item(self, item):
        if item:
            self.player.stop()
            self.gui.window.setWindowTitle("%s Lily Player:"  % item.name)
            self.player.open(item.filename)
            self.player.play()
        else:
            self.gui.window.setWindowTitle("Lily Player")
            self.player.stop()

    def goto_dlg(self):
        time = self.gui.do_input_dlg('Run command', 'Enter command', str(self.player.position))
        try:
            self.player.position = Time.parse(time)
        except ValueError:
            pass

    def about(self):
        libs = [ 
            ('Python', platform.python_version()),
            ('System', platform.system() + " " + platform.release()),
        ]
        libs.extend(self.player.versions())
        self.gui.do_about(authors=[__author__], version=__version__, libs=libs)

    def get_fullscreen(self):
        return self.gui.do_get_fullscreen()
    
    def set_fullscreen(self, value=None):
        if value is None:
            value = not self.gui.do_get_fullscreen()
        
        self.gui.do_set_fullscreen(value)

    def thumbinals(self, cols, rows, size, margin):
        count = rows * cols
        
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
                size=size, cols=cols, border=margin,
        )
        
        self.player.position_fraction = saved_pos
        self.player.state = saved_state


    def thumbinals_dialog(self):
        struct = self.gui.do_thumbinals_dialog(utils.Struct(cols=4, rows=10, size=200, margin=10))
        if struct is not None:
            s = struct
            self.thumbinals(s.cols, s.rows, s.size, s.margin)

    @args(arguments_table, 'thumbdlg')
    def cmd_thumb_dlg(self):
        self.thumbinals_dialog()

    @args(arguments_table, 'exit')
    def cmd_exit(self):
        # TODO: make this better
        exit()

    @args(arguments_table, 'about')
    def cmd_about(self):
        self.about()

    @args(arguments_table, 'cmddlg')
    def cmd_cmddlg(self):
        cmd = self.gui.do_input_dlg('Run command', 'Enter command')
        self.dispatch(cmd)
        
    @args(arguments_table, 'gotodlg')
    def cmd_gotodlg(self):
        self.goto_dlg()
    
    @args(arguments_table, 'open', StrArg())
    def cmd_open(self, url):
        self.open(url)
        
    @args(arguments_table, 'opendlg')
    def cmd_opendlg(self):
        self.open_dlg()
        #filename = QFileDialog.getOpenFileName(self.window, 'Open file', '/home/kosqx')
        #print filename
        #if filename:
            #self.player.open(str(filename))
    
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

    @args(arguments_table, 'thumb', IntArg(1, 10), IntArg(1, 100))
    def cmd_thumb(self, rows, cols):
        self.thumbinals(rows, cols, 200, 10)

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
        
    @args(arguments_table, 'fullscreen', EnumArg({'on': True, 'off': False}))
    def cmd_fullscreen_enum(self, enum):
        self.set_fullscreen(enum)

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
