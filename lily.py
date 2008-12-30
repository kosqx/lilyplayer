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


from PyQt4.QtCore import *
from PyQt4.QtGui import *


from play_time import Time
from player import Player
from arguments import PrefixArg, FloatArg, IntArg, TimeArg, StrArg, EnumArg, parse_arguments, args

import compose_thumbs

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

class MainWindow(object):
    arguments_table = []
    
    def dispatch(self, args):
        parsed = parse_arguments(self.arguments_table, args)
        parsed[0](*([self] + parsed[1:]))


    def on_timer(self):
        if self.player.state == 'finish':
            next = self.playlist.next()
            self.open_item(next)

    def open_item(self, item):
        if item:
            self.player.stop()
            self.window.setWindowTitle("%s Lily Player:"  % item.name)
            self.player.open(item.filename)
            self.player.play()
        else:
            self.window.setWindowTitle("Lily Player")
            self.player.stop()


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
    

    @args(arguments_table, 'speed', FloatArg(0.25, 4.0))
    def cmd_speed(self, val):
        self.player.speed = val
        
    @args(arguments_table, 'goto', FloatArg(0.0, 1.0))
    def cmd_goto_pos(self, val):
        self.player.position_fraction = val
    
    @args(arguments_table, 'goto', TimeArg())
    def cmd_goto_time(self, val):
        self.player.position = Time.parse(val)
    
    @args(arguments_table, 'volume', FloatArg(0.0, 1.0))
    def cmd_volume(self, val):
        self.player.volume = val
        
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
        self.do_set_fullscreen(None)
        
        
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

class Main(QApplication, MainWindow):
    def __init__(self): 
        QApplication.__init__(self, sys.argv)
        
        self.window = QWidget()
        self.window.setWindowTitle("Lily Player")
        self.window.setLayout(QVBoxLayout())
        self.window.layout().setMargin(0)
        self.window.layout().setSpacing(0)

        self.entry = QLineEdit(self.window)
        self.window.layout().addWidget(self.entry)
        self.connect(self.entry, SIGNAL("returnPressed()"), self.run)
        
        self.movie_window = QWidget(self.window)
        self.window.layout().addWidget(self.movie_window)
        
        self.window.resize(self.window.minimumSizeHint().expandedTo(QSize(600, 400)))
        self.window.show() 
        
        self.player = Player.create('gstreamer', self, self.movie_window.winId())

        QTimer.singleShot(0, self.autoopen)
        
        
    def autoopen(self):
        self.playlist = Playlist(sys.argv[1:])
        
        self.open_item(self.playlist.next())
        
        self.ctimer = QTimer()
        self.ctimer.start(1000)
        QObject.connect(self.ctimer, SIGNAL("timeout()"), self.on_timer)
        print 'autoopen'
        
    def run(self):
        text = str(self.entry.text())
        self.entry.setText('')
       
        self.dispatch(text)

    def do_set_fullscreen(self, value):
        if value is None:
            value = not self.window.isFullScreen()
            
        if value:
            self.window.showFullScreen()
        else:
            self.window.showNormal()

main = Main() 
main.exec_()
