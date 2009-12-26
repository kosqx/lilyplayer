#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Copyright (C) 2008,2009  Krzysztof Kosyl <krzysztof.kosyl@gmail.com>

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
import time
import logging


from lilyplayer.utils.arguments import PrefixArg, FloatArg, IntArg, TimeArg, StrArg, EnumArg
from lilyplayer.utils.arguments import Cmd, CmdNotFound
from lilyplayer.utils.arguments import prefix_value_change
import lilyplayer.utils.compose_thumbs as compose_thumbs
import lilyplayer.settings as settings


class Commands(object):
    cmd = Cmd()
    
    def __init__(self, controller):
        super(Commands, self).__init__()
        self.controller = controller
    
    def dispatch(self, command):
        method, args = self.cmd.parse(command)
        method(*([self] + args))
    
    @cmd(StrArg())
    def theme(self, name):
        settings.set('gui.theme', name)
        self.controller.signal.emit('theme')
            
    @cmd()
    def video_scale_dlg(self):
        result = self.controller.gui.do_input_dlg('Video scale', 'Enter scale')
        self.dispatch('video-scale ' + result)
    
    @cmd(FloatArg(0.2, 5.0))
    def video_scale(self, scale):
        self.controller.video_scale(scale)
    
    @cmd()
    def thumbdlg(self):
        self.controller.thumbinals_dialog()
    
    @cmd()
    def exit(self):
        self.controller.exit()
    
    @cmd()
    def about(self):
        self.controller.about()
    
    @cmd()
    def cmddlg(self):
        cmd = self.controller.gui.do_input_dlg('Run command', 'Enter command')
        self.dispatch(cmd)
    
    @cmd()
    def gotodlg(self):
        self.controller.goto_dlg()
    
    @cmd(StrArg())
    def open(self, url):
        self.controller.open(url)
    
    @cmd()
    def opendlg(self):
        self.controller.open_dlg()
    
    @cmd()
    def close(self):
        self.controller.player.close()
    
    @cmd(PrefixArg(['+', '-', '=', '']), FloatArg(0.25, 4.0))
    def speed(self, prefix, value):
        self.controller.player.speed = prefix_value_change(self.controller.player.speed, prefix, value)
    
    @cmd(PrefixArg(['+', '-', '=', '']), FloatArg(0.0, 1.0))
    def goto__pos(self, prefix, value):
        self.controller.player.position_fraction = prefix_value_change(self.controller.player.position_fraction, prefix, value)
    
    @cmd(PrefixArg(['+', '-', '=', '']), TimeArg())
    def goto__time(self, prefix, value):
        self.controller.player.position = prefix_value_change(self.controller.player.position, prefix, value)
    
    @cmd(PrefixArg(['+', '-', '=', '']), FloatArg(0.0, 1.0))
    def volume(self, prefix, value):
        self.controller.player.volume = prefix_value_change(self.controller.player.volume, prefix, value)
    
    @cmd()
    def mute(self):
        self.controller.player.mute = None
    
    @cmd()
    def snap(self):
        format, data = self.controller.player.snapshot()
        filename = os.path.expanduser('~/lily_%s.%s' % (time.strftime('%Y-%m-%d_%H:%M:%S'), format))
        fo = open(filename, 'wb')
        fo.write(data)
        fo.close()
    
    @cmd(IntArg(1, 10), IntArg(1, 100))
    def thumb(self, rows, cols):
        self.controller.thumbinals(rows, cols, 200, 10)
    
    @cmd()
    def play(self):
        self.controller.player_play()
    
    @cmd()
    def pause(self):
        self.controller.player_pause()
    
    @cmd()
    def stop(self):
        self.controller.player_stop()
    
    @cmd()
    def toggle(self):
        self.controller.player_toggle()
    
    @cmd(EnumArg({'on': True, 'off': False}))
    def fullscreen__enum(self, enum):
        self.controller.set_fullscreen(enum)
    
    @cmd()
    def fullscreen(self):
        self.controller.set_fullscreen(None)
    
    @cmd()
    def playlist_next(self):
        self.controller.open_item(self.controller.playlist.next())
    
    @cmd(EnumArg(['repeat-one', 'repeat', 'shuffle', 'default']))
    def playlist_mode(self, mode):
        """ Changes playlist mode to specified """
        self.controller.playlist.mode = mode
    
    @cmd(IntArg(0))
    def playlist_goto(self, index):
        """ Changes playlist current item do specified """
        self.controller.playlist_goto(index)
        
    @cmd(EnumArg({'on': True, 'off': False, 'toggle': None}))
    def view_sidebar(self, enum):
        self.controller.view_sidebar(enum)

