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


    def on_timer(self):
        if self.player.state == 'finish':
            next = self.playlist.next()
            self.open_item(next)
        #self.slider.setValue(int(self.player.position_fraction * 1000))
        self.controls._redraw(self)

    def open_item(self, item):
        if item:
            self.player.stop()
            self.window.setWindowTitle("%s Lily Player:"  % item.name)
            self.player.open(item.filename)
            self.player.play()
        else:
            self.window.setWindowTitle("Lily Player")
            self.player.stop()

    def get_fullscreen(self):
        return self.do_get_fullscreen()
    
    def set_fullscreen(self, value=None):
        if value is None:
            value = not self.do_get_fullscreen()
        
        self.do_set_fullscreen(value)



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

class PlayControls(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.main = None
        self.actions = {}
        
        pos_data = """
        0    0   7
        1    7   7
        2   14   7
        3   21   7
        4   28   7
        5   35   7
        6   42   7
        7   49   7
        8   56   7
        9   63   7
        :   70   7
        (   77   7
        )   84   7
        _   91   7
        p   98  16    play sign
        P  114  16    pause sign
        m  130  16    sound on
        M  146  16    sound off
        f  162  16    normal screen
        F  178  16    full screen
        {  194   5
        #  199   5
        }  204   5
        [  209   5
        =  214   5
        ]  219   5
        """
        
        self._pos = {}
        for line in pos_data.splitlines():
            parts = line.split()
            if parts:
                self._pos[parts[0]] = (int(parts[1]), int(parts[2]))
        if '_' in self._pos:
            self._pos[' '] = tuple(self._pos['_'])
            
        assert self._pos['['][1] == self._pos[']'][1]
        assert self._pos['['][1] == self._pos['{'][1]
        assert self._pos[']'][1] == self._pos['}'][1]
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self._pixmap = QPixmap('/home/kosqx/newc.png')

        
    def _makeSpec(self, time, duration, position, volume, play='p', mute='m', full='f'):
        spec = []
        self.actions = {}
        
        left = 0
        right = self.width()
        
        def from_left(spec, left, c, name=None):
            x, l = self._pos[c]
            spec.append((x, l, left, l))
            if name:
                self.actions[name] = (left, left + l)
            return left + l
        
        def from_right(spec, right, c, name=None):
            x, l = self._pos[c]
            spec.append((x, l, right - l, l))
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
            spec.append(self._pos['#'] + (left, done_size))
            spec.append(self._pos['='] + (left + done_size, bar_size - done_size))

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

        return spec
        
    def _drawSpec(self, painter, spec):
        H = self._pixmap.height()
        for img_offset, img_size, draw_offset, draw_size in spec:
            painter.drawPixmap(
                QRect(draw_offset, 0, draw_size, H),
                self._pixmap,
                QRect(img_offset, 0, img_size, H)
            )
        
    def _command(self, name, x, size):
        if self.main is not None:
            if name == 'mute':
                self.main.player.mute = None
            elif name == 'play':
                self.main.player.toggle()
            elif name == 'full':
                self.main.set_fullscreen()
            elif name == 'volume':
                self.main.player.volume = 1.0 * x / (size - 1)
            elif name == 'position':
                self.main.player.position_fraction = 1.0 * x / (size - 1)
                
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
    
    def _redraw(self, main):
        self.main = main
        self.update()
    
    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        d = dict(time='00:00:00', duration='00:00:00', position=0.0, volume=1.0, play='p', mute='m', full='f')
        
        if self.main is None:
            pass
        else:
            player = self.main.player
            d['time']     = str(player.position)
            d['duration'] = str(player.duration)
            d['position'] = player.position_fraction
            d['volume']   = player.volume
            d['play']     = 'pP'[player.state == 'play']
            d['mute']     = 'mM'[player.mute]
            d['full']     = 'fF'[self.main.get_fullscreen()]

        spec = self._makeSpec(**d)
        self._drawSpec(painter, spec)

    def keyPressEvent(self, event):
        print 'keyPress'

def key_event_to_str(event):
    mods = ''
    
    if event.modifiers() & Qt.AltModifier:
        mods += 'Alt+'
    if event.modifiers() & Qt.ControlModifier:
        mods += 'Ctrl+'
    if event.modifiers() & Qt.ShiftModifier:
        mods += 'Shift+'
    if event.modifiers() & Qt.MetaModifier:
        mods += 'Meta+'
    
    keys = {
        Qt.Key_Backspace: 'Backspace',
        Qt.Key_Tab:       'Tab',
        Qt.Key_Return:    'Enter',
        Qt.Key_Escape:    'Esc',
        Qt.Key_Space:     'Space',
        
        Qt.Key_Insert:    'Insert',
        Qt.Key_Delete:    'Delete',
        Qt.Key_PageUp:    'PageUp',
        Qt.Key_PageDown:  'PageDown',
        Qt.Key_End:       'End',
        Qt.Key_Home:      'Home',
        
        Qt.Key_Left:      'Left',
        Qt.Key_Up:        'Up',
        Qt.Key_Right:     'Right',
        Qt.Key_Down:      'Down',
        
        Qt.Key_F1:        'F1',
        Qt.Key_F2:        'F2',
        Qt.Key_F3:        'F3',
        Qt.Key_F4:        'F4',
        Qt.Key_F5:        'F5',
        Qt.Key_F6:        'F6',
        Qt.Key_F7:        'F7',
        Qt.Key_F8:        'F8',
        Qt.Key_F9:        'F9',
        Qt.Key_F10:       'F10',
        Qt.Key_F11:       'F11',
        Qt.Key_F12:       'F12',
        
        Qt.Key_NumLock:   'Num Lock',
        Qt.Key_ScrollLock:'Scroll Lock'
    }
    
    ekey = event.key()
    key = None
    
    if ekey in keys:
        key = keys[ekey]
    elif ord('a') <= ekey <= ord('z'):
        key = chr(ekey).upper()
    elif ord('A') <= ekey <= ord('Z'):
        key = chr(ekey).upper()
    elif ord('0') <= ekey <= ord('9'):
        key = chr(ekey)
        
    if key is not None:
        return mods + key
    else:
        return None

class GuiMainWindow(QMainWindow):
    def keyPressEvent(self, event):
        keys = key_event_to_str(event)
        event.accept()
        if keys is not None:
            self.emit(SIGNAL('myKey(QString)'), QString(keys))
   
    def wheelEvent (self, event):
        """
        Qt.MouseButtons buttons (self)
        int delta (self)
        Qt.Orientation orientation (self)
        """
        print 'whell', event.globalPos(), event.delta()
        event.accept()
        if event.delta() < 0:
            keys = 'WheelDown'
        else:
            keys = 'WheelUp'
        self.emit(SIGNAL('myKey(QString)'), QString(keys))
        
    def mouseDoubleClickEvent (self, event):
        """
        Qt.MouseButton button (self)
        Qt.MouseButtons buttons (self)
        bool hasExtendedInfo (self)

        """
        event.accept()
        print 'double', event.globalPos()
    
    def contextMenuEvent(self, event):
        """
        Reason reason (self)
        """
        event.accept()
        print 'context', event.globalPos()
        
class Main(QApplication, Controler):
    def __init__(self): 
        QApplication.__init__(self, sys.argv)
        
        self.window = GuiMainWindow()
        self.central = QWidget()
        self.window.setCentralWidget(self.central)
        #self.window = QMainWindow()
        self.window.setWindowTitle("Lily Player")
        self.central.setLayout(QVBoxLayout())
        self.central.layout().setMargin(0)
        self.central.layout().setSpacing(0)

        self.connect(self.window, SIGNAL('myKey(QString)'), self.key)

        self.entry = QLineEdit(self.window)
        self.central.layout().addWidget(self.entry)
        self.connect(self.entry, SIGNAL("returnPressed()"), self.run)
        self.entry.setVisible(False)

        self.movie_window = QWidget(self.window)
        #self.movie_window.palette().background().setColor(Qt.blue)
        #self.movie_window.setStyleSheet("background-color:black")
        self.movie_window.setAutoFillBackground(True)
        
        palette = self.movie_window.palette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.Inactive, QPalette.Window, QColor(0, 0, 0))
        
        self.movie_window.setPalette(palette)
        
        self.central.layout().addWidget(self.movie_window)
        
        self.controls = PlayControls(self.window)
        self.central.layout().addWidget(self.controls)
        
        #self.slider = QSlider(Qt.Horizontal, self.window)
        #self.slider.setRange (0, 1000)
        #self.connect(self.slider,  SIGNAL('sliderReleased()'), self.gui_goto)
        #self.window.layout().addWidget(self.slider)
        
        self.window.resize(self.window.minimumSizeHint().expandedTo(QSize(600, 400)))
        self.window.show() 
        #self.window_base.show() 
        
        self.player = Player.create('gstreamer', self, self.movie_window.winId())

        QTimer.singleShot(0, self.autoopen)
        
        self.create_menu([
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
        ])
    
    def key(self, keys):
        self.keyboard_shortcut(str(keys))

        
    def autoopen(self):
        self.playlist = Playlist(sys.argv[1:])
        
        self.open_item(self.playlist.next())
        
        self.ctimer = QTimer()
        self.ctimer.start(250)
        QObject.connect(self.ctimer, SIGNAL("timeout()"), self.on_timer)
        print 'autoopen'
        
    def run(self):
        text = str(self.entry.text())
        self.entry.setText('')
       
        self.dispatch(text)
    
    def do_get_fullscreen(self):
        return self.window.isFullScreen()

    def do_set_fullscreen(self, value):
        #self.entry.setVisible(not value)
        self.window.menuBar().setVisible(not value)
        
        if value:
            self.window.showFullScreen()
        else:
            self.window.showNormal()

    def gui_goto(self):
        value = float(self.slider.value())
        self.player.position_fraction = value / 1000
        
    def create_menu(self, data):
        def add(root, data):
            for item in data:
                if item is None:
                    root.addSeparator()
                elif isinstance(item, (tuple, list)):
                    menu = root.addMenu(item[0])
                    add(menu, item[1])
                else:
                    root.addAction(item)
        
        menu_bar = self.window.menuBar()
        add(menu_bar, data)


    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

if __name__ == '__main__':
    main = Main() 
    main.exec_()
