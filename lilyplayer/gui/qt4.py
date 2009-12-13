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


import sys
import os.path
import thread
import logging


from PyQt4.QtCore import *
from PyQt4.QtGui import *



import lilyplayer.settings as settings
import lilyplayer.utils.utils as utils

from qt4_keys import key_event_to_str
from qt4_controls import PlayControls
from qt4_markup import GuiMarkupWindow
from qt4_sidebar import GuiSidebar


class GuiMainWindow(QMainWindow):
    def __init__(self, controller):
        QMainWindow.__init__(self)
        self.setMouseTracking(True)
        self.controller = controller
    
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
        logging.debug('whellEvent %r %r' % (event.globalPos(), event.delta()))
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
        # TODO: doubleClick(x,y)
        # self.emit(SIGNAL('doubleClick()'))
        self.controller.set_fullscreen()
        logging.debug('doubleClickEvent %r' % event.globalPos())
    
    def contextMenuEvent(self, event):
        """
        Reason reason (self)
        """
        event.accept()
        logging.debug('contextMenuEvent %r' % event.globalPos())


    def mouseMoveEvent(self, event):
        logging.debug('mouseMoveEvent %r %r' % (event.x(), event.y()))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = [unicode(i.path()) for i in event.mimeData().urls()]
            event.acceptProposedAction()
            event.setDropAction(Qt.CopyAction)
            logging.debug('dropEvent urls: %r' % urls)
            #TODO: method to append many and go
            #self.controller.open(urls[0])
            self.controller.playlist_add_and_goto(urls)


class GuiMovieWindow(QWidget):
    def __init__(self, parent, controller):
        QMainWindow.__init__(self, parent)
        self.setMouseTracking(True)
        self.controller = controller
        
        self.setAcceptDrops(True)
        
        self.setMouseTracking(True)
        self.setAutoFillBackground(True)
        
        
        palette = self.palette()
        palette.setColor(QPalette.Active, QPalette.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.Inactive, QPalette.Window, QColor(0, 0, 0))
        
        self.setPalette(palette)
        
        
class GuiThumbinalDialog(object):
    def __init__(self, parent=None):
        self.dialog = QDialog(parent)
        self.dialog.setWindowTitle("Thumbinals")
        
        grid = QGridLayout()
        
        self.colsSpinBox = QSpinBox(self.dialog)
        self.colsSpinBox.setRange(1, 10)
        colsLabel = QLabel('Number of columns', self.dialog)
        grid.addWidget(colsLabel,        0, 0)
        grid.addWidget(self.colsSpinBox, 0, 1)

        self.rowsSpinBox = QSpinBox(self.dialog)
        self.rowsSpinBox.setRange(1, 40)
        rowsLabel = QLabel('Number of rows', self.dialog)
        grid.addWidget(rowsLabel,        0, 2)
        grid.addWidget(self.rowsSpinBox, 0, 3)
        
        self.sizeSpinBox = QSpinBox(self.dialog)
        self.sizeSpinBox.setRange(100, 2000)
        self.sizeSpinBox.setSingleStep(10)
        sizeLabel = QLabel('Thumbinal size', self.dialog)
        grid.addWidget(sizeLabel,        1, 0)
        grid.addWidget(self.sizeSpinBox, 1, 1)
        
        self.marginSpinBox = QSpinBox(self.dialog)
        self.marginSpinBox.setRange(0, 20)
        marginLabel = QLabel('Margin', self.dialog)
        grid.addWidget(marginLabel,        1, 2)
        grid.addWidget(self.marginSpinBox, 1, 3)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        grid.addWidget(buttonBox, 2, 0, 1, 4)
        
        self.dialog.connect(buttonBox, SIGNAL("accepted()"), self.dialog, SLOT("accept()"))
        self.dialog.connect(buttonBox, SIGNAL("rejected()"), self.dialog, SLOT("reject()"))
        
        self.dialog.setLayout(grid)

        
    def run(self, defaults):
        d = defaults
        self.colsSpinBox.setValue(d.cols)
        self.rowsSpinBox.setValue(d.rows)
        self.sizeSpinBox.setValue(d.size)
        self.marginSpinBox.setValue(d.margin)
        
        if self.dialog.exec_():
            return utils.Struct(
                cols=self.colsSpinBox.value(),
                rows=self.rowsSpinBox.value(),
                size=self.sizeSpinBox.value(),
                margin=self.marginSpinBox.value(),
            )
        else:
            return None

    
#QWidget.contextMenuEvent (self, QContextMenuEvent)

class GuiMain(QApplication):
    def __init__(self, controller=None): 
        QApplication.__init__(self, sys.argv)
        
        self.controller = controller

        
        
        self.setWindowIcon(QIcon(settings.get_path('data', 'mainicon.png')))
        
        self.window = GuiMainWindow(self.controller)
        
        # work - only on systems with support of this
        #self.window.setWindowOpacity(0.5)
        
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

        

        self.movie_window = GuiMovieWindow(self.window, self.controller)
        
        self.markup_window = GuiMarkupWindow(self.movie_window)
        self.markup_window.set_style({'font-size': 32, 'border-width': 1})
        #self.markup_window.render('Ala ma kota<br/>i psa', {'font-size': '32'})
        #self.markup_window.setParent(self.movie_window, Qt.Tool)
        self.markup_window.show()
        
        self.sidebar = GuiSidebar(self.window, controller)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.movie_window)
        self.splitter.addWidget(self.sidebar)
        
        self.central.layout().addWidget(self.splitter)
        
        self.controls = PlayControls(self.window, self.controller)
        self.central.layout().addWidget(self.controls)
        
        self.window.setAcceptDrops(True)
        
        self.window.resize(self.window.minimumSizeHint().expandedTo(QSize(600, 400)))
        self.window.show() 

        QTimer.singleShot(0, self.autoopen)
        
        self.markup_timer = QTimer()
        self.markup_timer.start(200)
        QObject.connect(self.markup_timer, SIGNAL("timeout()"), self.on_markup_timer) 
    
    def key(self, keys):
        self.controller.keyboard_shortcut(str(keys))

    def autoopen(self):
        self.controller.on_start()

        self.ctimer = QTimer()
        self.ctimer.start(250)
        QObject.connect(self.ctimer, SIGNAL("timeout()"), self.on_timer)
    
    def on_timer(self):
        self.controller.on_timer()
        
    def on_markup_timer(self):
        pass
        import time
        #print self.movie_window.height(), self.markup_window.height()
        
        #self.markup_window.set_text('%s' % time.strftime('%H:%M:%S'))
        self.markup_window.set_text(self.controller.get_current_subtitle())
        
        x = self.movie_window.width() - self.markup_window.width()
        y = self.movie_window.height() - self.markup_window.height()
        point = self.movie_window.mapToGlobal(QPoint(x/2, y))
        self.markup_window.move(point)
        
    def run(self):
        text = str(self.entry.text())
        self.entry.setText('')
       
        self.controller.dispatch(text)
        
    def do_set_title(self, title):
        self.window.setWindowTitle(title)
    
    def do_resize_video_window(self, width, height):
        request_size = QSize(width, height)
        movie_size = self.movie_window.size()
        window_size = self.window.size()
        new_size = window_size + request_size - movie_size
        
        self.window.resize(new_size)
        
    def do_get_fullscreen(self):
        return self.window.isFullScreen()

    def do_set_fullscreen(self, value):
        #self.entry.setVisible(not value)
        self.window.menuBar().setVisible(not value)
        
        if value:
            self.old_size = self.window.size()
        
        if value:
            self.window.showFullScreen()
        else:
            self.window.showNormal()
        
        if not value and hasattr(self, 'old_size'):
            self.window.resize(self.old_size)
    
    def do_get_view_sidebar(self):
        return self.sidebar.isVisible()

    def do_set_view_sidebar(self, value):
        movie_w = self.movie_window.width()
        total_w = self.splitter.width()
        window_w = self.window.width()
        height = self.window.height()

        if value:
            new_size = QSize(window_w + self._last_sidebar_width, height)
        else:
            self._last_sidebar_width = total_w - movie_w
            new_size = QSize(window_w - self._last_sidebar_width, height)
        
        self.sidebar.setVisible(value)
        self.window.resize(new_size)    
            
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
            
            
    def do_thumbinals_dialog(self, defaults):
        dlg = GuiThumbinalDialog(self.window)
        return dlg.run(defaults)

            
    def do_input_dlg(self, title, label, text=''):
        result, ok = QInputDialog.getText(self.window, QString(title), QString(label), QLineEdit.Normal, QString(text))
        if ok:
            return unicode(result)
        else:
            return None
            
    def do_about(self, authors, version, libs=[]):
        libs = libs + [
            ('Qt',   QT_VERSION_STR),
            ('PyQt', PYQT_VERSION_STR),
        ]
        
        QMessageBox.about(self.window, "About Lily Player",
                """<b>Lily Player</b> v%(version)s
                <p>Copyright &copy; 2008,2009 %(authors)s.</p>
                <br/><br/>
                Software versions:
                <table>v%(libs)s</table>
                """ % {
                    'version': '.'.join(str(i) for i in version), 
                    'authors': ', '.join(str(i) for i in authors),
                    'libs':    '\n'.join('<tr><td>%s&nbsp;</td><td>%s</td></tr>' % lib for lib in libs) 
                })
    
    
    def on_menu_item(self, cmd, *skip):
        self.controller.dispatch(cmd)

    def update_menu(self, data):
        def add(root, data):
            for item in data:
                if item.is_separator():
                    root.addSeparator()
                elif item.is_submenu():
                    menu = root.addMenu(item.text)
                    add(menu, item.submenu)
                elif item.is_item():
                    action = root.addAction(item.text)
                    self.connect(action, SIGNAL("triggered()"), utils.FunctionWithParams(self.on_menu_item, item.cmd))
        
        menu_bar = self.window.menuBar()
        menu_bar.clear()
        add(menu_bar, data.submenu)


