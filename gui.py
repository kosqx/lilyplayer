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
import os.path


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import settings
import utils


class PlayControls(QWidget):
    def __init__(self, parent, controler):
        QWidget.__init__(self, parent)
        self.controler = controler
        self.actions = {}
        
        pos_data = utils.File(settings.get_path('data', 'controls.txt')).read()
        
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
        self._pixmap = QPixmap(settings.get_path('data', 'controls.png'))

        
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
        
        Qt.Key_CapsLock:  'CapsLock',
        Qt.Key_NumLock:   'NumLock',
        Qt.Key_ScrollLock:'ScrollLock',
        
        Qt.Key_Exclam:       'Exclam',       # !
        Qt.Key_At:           'At',           # @
        Qt.Key_NumberSign:   'Hash',         # #
        Qt.Key_Dollar:       'Dollar',       # $
        Qt.Key_Percent:      'Percent',      # %
        Qt.Key_AsciiCircum:  'Caret',        # ^
        Qt.Key_Ampersand:    'Ampersand',    # &
        Qt.Key_Asterisk:     'Asterisk',     # *

        Qt.Key_ParenLeft:    'ParenLeft',    # (
        Qt.Key_ParenRight:   'ParenRight',   # )
        Qt.Key_BracketLeft:  'BracketLeft',  # [
        Qt.Key_BracketRight: 'BracketRight', # ]
        Qt.Key_BraceLeft:    'BraceLeft',    # {
        Qt.Key_BraceRight:   'BraceRight',   # }
        Qt.Key_Less:         'Less',         # <
        Qt.Key_Greater:      'Greater',      # >
        
        Qt.Key_AsciiTilde:   'Tilde',        # ~
        Qt.Key_QuoteLeft:    'Grave',        # `
        
        Qt.Key_Underscore:   'Underscore',   # _
        Qt.Key_Minus:        'Minus',        # -
        
        Qt.Key_Plus:         'Plus',         # +
        Qt.Key_Equal:        'Equal',        # =
        
        Qt.Key_Bar:          'Pipe',          # |
        Qt.Key_Backslash:    'Backslash',    # \
        
        Qt.Key_Colon:        'Colon',        # :
        Qt.Key_Semicolon:    'Semicolon',    # ;
        
        Qt.Key_QuoteDbl:     'Quote',        # "
        Qt.Key_Apostrophe:   'Apostrophe',   # '
        
        Qt.Key_Comma:        'Comma',        # ,
        Qt.Key_Period:       'Dot',          # .
        
        Qt.Key_Question:     'Question',     # ?
        Qt.Key_Slash:        'Slash',        # /
        
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
    
    #print mods, key
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
        
        
class Main(QApplication):
    def __init__(self, controler=None): 
        QApplication.__init__(self, sys.argv)
        
        #self.controler = Controler()
        self.controler = controler
        
        self.setWindowIcon(QIcon(settings.get_path('data', 'mainicon.png')))
        
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
        
        self.controls = PlayControls(self.window, self.controler)
        self.central.layout().addWidget(self.controls)
        
        #self.slider = QSlider(Qt.Horizontal, self.window)
        #self.slider.setRange (0, 1000)
        #self.connect(self.slider,  SIGNAL('sliderReleased()'), self.gui_goto)
        #self.window.layout().addWidget(self.slider)
        
        self.window.resize(self.window.minimumSizeHint().expandedTo(QSize(600, 400)))
        self.window.show() 
        #self.window_base.show() 
        
        

        QTimer.singleShot(0, self.autoopen)
    
    def key(self, keys):
        self.controler.keyboard_shortcut(str(keys))

    def autoopen(self):
        self.controler.on_start()

        self.ctimer = QTimer()
        self.ctimer.start(250)
        QObject.connect(self.ctimer, SIGNAL("timeout()"), self.on_timer)
    
    def on_timer(self):
        self.controler.on_timer()
        
    def run(self):
        text = str(self.entry.text())
        self.entry.setText('')
       
        self.controlerdispatch(text)
    
    def do_get_fullscreen(self):
        return self.window.isFullScreen()

    def do_set_fullscreen(self, value):
        #self.entry.setVisible(not value)
        self.window.menuBar().setVisible(not value)
        
        if value:
            self.window.showFullScreen()
        else:
            self.window.showNormal()
            
    def do_file_dialog(self, title, mode='open', path=None, filter=None):
        if path is None:
            path = os.path.expanduser('~')
        else:
            path = path
      
        if filter is None:
            filter = ''
        else:
            filter = ';;'.join('%s (%s)' % (name, ' '.join(exts)) for name, exts in filter)
        if mode == 'save':
            return unicode(QFileDialog.getSaveFileName(self.window, QString(title), QString(path), QString(filter)))
        elif mode == 'open':
            return unicode(QFileDialog.getOpenFileName (self.window, QString(title), QString(path), QString(filter)))
        elif mode == 'open_many':
            filelist = QFileDialog.getOpenFileName (self.window, QString(title), QString(path), QString(filter))
            return [unicode(filelist[i]) for i in xrange(len(filelist))]
            
    def do_input_dlg(self, title, label, text=''):
        result, ok = QInputDialog.getText(self.window, QString(title), QString(label), QLineEdit.Normal, QString(text))
        if ok:
            return unicode(result)
        else:
            return None
            
    def do_about(self, authors, version):
        QMessageBox.about(self.window, "About Lily Player",
                """<b>Lily Player</b> v %(version)s
                <p>Copyright &copy; 2008,2009 %(authors)s.</p>
                
                <table>
                    <tr><td>Python</td><td>2.5</td></tr>
                    <tr><td>Qt  </td><td>4.4.2</td></tr>
                    <tr><td>PyQt</td><td>4.3</td></tr>
                    <tr><td>GStreamer</td><td>0.10.2</td></tr>
                </table>
                """ % {
                    'version': '.'.join(str(i) for i in version), 
                    'authors': ', '.join(str(i) for i in authors), 
                })
                
                
                #"""<p>Python %s - Qt %s - PyQt %s on %s""" % (
                #platform.python_version(),
                #QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))
        
    def update_menu(self, data):
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
        menu_bar.clear()
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

