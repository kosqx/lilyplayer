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


from PyQt4.QtCore import *
from PyQt4.QtGui import *


import lilyplayer.settings as settings
import lilyplayer.utils.utils as utils


class PlayControls(QWidget):
    def __init__(self, parent, controler):
        QWidget.__init__(self, parent)
        
        self.setAcceptDrops(True)
        
        self.controler = controler
        self.actions = {}
        
        pos_data = utils.File(settings.get_path('themes', settings.get('gui.theme'), 'controls.txt')).read()
        
        self._pos = {}
        for line in pos_data.splitlines():
            parts = line.split()
            if parts and not parts[0].startswith('#'):
                self._pos[parts[0]] = (int(parts[1]), int(parts[2]))
        if '_' in self._pos:
            self._pos[' '] = tuple(self._pos['_'])
            
        assert self._pos['['][1] == self._pos[']'][1]
        assert self._pos['['][1] == self._pos['{'][1]
        assert self._pos[']'][1] == self._pos['}'][1]
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self._pixmap = QPixmap(settings.get_path('themes', settings.get('gui.theme'), 'controls.png'))

        
    def _makeSpec(self, time, duration, position, volume, play='p', mute='m', full='f'):
        def from_left(spec, left, c, name=None):
            x, l = self._pos[c]
            spec.append((left, l, x, l))
            if name:
                self.actions[name] = (left, left + l)
            return left + l
        
        def from_right(spec, right, c, name=None):
            x, l = self._pos[c]
            spec.append((right - l, l, x, l))
            if name:
                self.actions[name] = (right - l, right)
            return right - l
        
        def bar(spec, left, right, value, name=None):
            ch_l = ['{', '['][int(value == 0.0)]
            ch_r = [']', '}'][int(value == 1.0)]
            ch_size = self._pos['['][1]
            
            left = from_left(spec, left, ch_l)
            right = from_right(spec, right, ch_r)
            if name:
                self.actions[name] = (left, right)
            
            bar_size = right - left
            done_size = int(value * bar_size + 0.5)
            spec.append((left, done_size) + self._pos['$'])
            spec.append((left + done_size, bar_size - done_size) + self._pos['='])
            
        spec = []
        self.actions = {}
        
        left = 0
        right = self.width()

        left = from_left(spec, left, '(')
        left = from_left(spec, left, play, name='play')
        for c in (' ' + time):
            left = from_left(spec, left, c)
        
        right = from_right(spec, right, ')')
        right = from_right(spec, right, full, name='full')
        right = from_right(spec, right, ' ')
        
        bar(spec,right - 50, right, volume, name='volume')
        right -= 50
        
        right = from_right(spec, right, mute, name='mute')
        for c in (duration + ' ')[::-1]:
            right = from_right(spec, right, c)
        
        bar(spec,left, right, position, name='position')

        return sorted(spec)
        
    def _drawSpec(self, painter, spec):
        H = self._pixmap.height()
        for draw_offset, draw_size, img_offset, img_size in spec:
            painter.drawPixmap(
                QRect(draw_offset, 0, draw_size, H),
                self._pixmap,
                QRect(img_offset, 0, img_size, H)
            )
            
        
        
    def _command(self, name, x, size):
        if self.controler is not None:
            if name == 'mute':
                self.controler.player.mute = None
            elif name == 'play':
                self.controler.player.toggle()
            elif name == 'full':
                self.controler.set_fullscreen()
            elif name == 'volume':
                self.controler.player.volume = 1.0 * x / (size - 1)
            elif name == 'position':
                self.controler.player.position_fraction = 1.0 * x / (size - 1)
                
            self.update()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.x()
            for name in self.actions:
                left, right = self.actions[name]
                if left <= x < right:
                    self._command(name, x - left, right - left)
            
            event.accept()
        else:
            QWidget.mousePressEvent(self, event)

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        return QSize(320, self._pixmap.height())
    
    def _redraw(self, controler):
        self.controler = controler
        self.update()
    
    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        d = dict(time='00:00:00', duration='00:00:00', position=0.0, volume=1.0, play='p', mute='m', full='f')
        
        if self.controler is None:
            pass
        else:
            player = self.controler.player
            d['time']     = str(player.position)
            d['duration'] = str(player.duration)
            d['position'] = player.position_fraction
            d['volume']   = player.volume
            d['play']     = 'pP'[player.state == 'play']
            d['mute']     = 'mM'[player.mute]
            d['full']     = 'fF'[self.controler.get_fullscreen()]

        spec = self._makeSpec(**d)
        self._drawSpec(painter, spec)
 
