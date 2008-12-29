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


import sys, os, os.path


from PyQt4.QtCore import *
from PyQt4.QtGui import *


from play_time import Time
from player import Player
from arguments import PrefixArg, FloatArg, IntArg, TimeArg, StrArg, EnumArg, parse_arguments, args




class MainWindow(object):
    arguments_table = []
    
    def dispatch(self, args):
        #if isinstance(args, basestring):
            #args = args.split()
        
        #print self.arguments_table
        parsed = parse_arguments(self.arguments_table, args)
        parsed[0](*([self] + parsed[1:]))
        
        #method_name = 'cmd_' + args[0].replace('-', '_')
        #if hasattr(self, method_name):
            #getattr(self, method_name)(*args[1:])

    @args(arguments_table, 'exit')
    def cmd_exit(self):
        # TODO: make this better
        exit()

    @args(arguments_table, 'open', StrArg())
    def cmd_open(self, url):
        self.player.open(parts[1])
        
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
        self.player.speed = float(val)
        
    @args(arguments_table, 'goto', FloatArg(0.0, 1.0))
    def cmd_goto_pos(self, val):
        self.player.position_fraction = float(val)
    
    @args(arguments_table, 'goto', TimeArg())
    def cmd_goto_time(self, val):
        self.player.position = Time.parse(val)
    
    @args(arguments_table, 'volume', FloatArg(0.0, 1.0))
    def cmd_volume(self, val):
        self.player.volume = val
    
    @args(arguments_table, 'snap')
    def cmd_snap(self):
        self.player.snapshot()

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
    

class Main(QApplication, MainWindow):
    def __init__(self): 
        QApplication.__init__(self, sys.argv)
        
        self.window = QWidget()
        self.window.setWindowTitle("Lily Player")
        self.window.setLayout(QVBoxLayout())
        self.window.layout().setMargin(0)
        self.window.layout().setSpacing(0)
        
        upper = QWidget(self.window)
        upper.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.window.layout().addWidget(upper)
        upper.setLayout(QHBoxLayout())
        upper.layout().setMargin(0)
        
        self.entry = QLineEdit(upper)
        upper.layout().addWidget(self.entry)
        self.connect(self.entry, SIGNAL("returnPressed()"), self.run)
        
        #self.button = QPushButton("Run", upper)
        #upper.layout().addWidget(self.button)
        #self.connect(self.button, SIGNAL("clicked()"), self.run)
        
        self.movie_window = QWidget(self.window)
        self.window.layout().addWidget(self.movie_window)
        
        self.window.resize(self.window.minimumSizeHint().expandedTo(QSize(600, 400)))
        self.window.show() 
        
        self.player = Player.create('gstreamer', self, self.movie_window.winId())

        QTimer.singleShot(0, self.autoopen)
        
    def autoopen(self):
        if len(sys.argv) > 1:
            self.player.open(os.path.abspath(sys.argv[1]))
        
    def run(self):
        text = str(self.entry.text())
        self.entry.setText('')
        
        self.dispatch(text)


main = Main() 
main.exec_()
