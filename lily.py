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


class MainWindow(object):
    def dispatch(self):
        pass

class Main(QApplication): 
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

        
    def run(self):
        text = str(self.entry.text())
        self.entry.setText('')
        parts = text.split(' ', 1)
        if parts[0] == "open":
            self.player.open(parts[1])
        elif parts[0] == "opendlg":
            filename = QFileDialog.getOpenFileName(self.window, 'Open file', '/home/kosqx')
            print filename
            if filename:
                self.player.open(str(filename))
        elif parts[0] == "toggle":
            self.player.toggle()
        elif parts[0] == "goto":
            self.player.position = Time.parse(parts[1])
        elif parts[0] == "speed":
            self.player.speed = float(parts[1])
        elif parts[0] == "pos":
            self.player.position_fraction = float(parts[1])
        elif parts[0] == "volume":
            self.player.volume = float(parts[1])
        elif parts[0] == "snap":
            self.player.snapshot()


main = Main() 
main.exec_()
