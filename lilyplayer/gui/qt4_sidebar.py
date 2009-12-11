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

import logging


from PyQt4.QtCore import *
from PyQt4.QtGui import *


import lilyplayer.info.imdb_info as imdb_info

from lilyplayer.gui.qt4_utils import create_action


import sys
if sys.version_info[:2] < (2, 5):
    def partial(func, arg):
        def callme():
            return func(arg)
        return callme
else:
    from functools import partial



class PlaylistModel(QAbstractTableModel):

    def __init__(self, controller):
        super(PlaylistModel, self).__init__()
        self.controller = controller
        self.playlist = controller.playlist
        self.dirty = False
        self.columns = {
            'name': 0,
            'filename': 1,
        }


    def data(self, index, role=Qt.DisplayRole):
        #print self.playlist.items
        
        if not index.isValid() or not (0 <= index.row() < len(self.playlist)):
            return QVariant()
        
        item = self.playlist[index.row()]
        
        
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 0:
                return QVariant(item.name)
            elif column == 1:
                return QVariant(item.filename)
            #elif column == TEU:
                #return QVariant(QString("%L1").arg(ship.teu))
                
        elif role == Qt.TextAlignmentRole:
            #if column == TEU:
                #return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        
        elif role == Qt.TextColorRole:
            return QVariant(QColor(Qt.black))
        elif role == Qt.BackgroundColorRole:
            if self.playlist.current == index.row():
                return QVariant(QColor(250, 230, 250))
            return QVariant(QColor(210, 230, 230))
        return QVariant()


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 0:
                return QVariant("Name")
            elif section == 1:
                return QVariant("Filename")
           
        return QVariant(int(section + 1))


    def rowCount(self, index=QModelIndex()):
        logging.debug('playlist length: %r' % len(self.playlist))
        return len(self.playlist)


    def columnCount(self, index=QModelIndex()):
        return 2
    
    def signal_doubleClicked(self, index):
        self.controller.playlist_goto(index.row())


class NiceSlider(QWidget):
    def __init__(self, label_code=None, value_code=None, parent=None):
        super(NiceSlider, self).__init__(parent)

        
        self.label = QLabel('Value', self)
        self.slider = QSlider(Qt.Horizontal, self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        #self.label.setStyleSheet('background-color:red')
        #self.slider.setStyleSheet('background-color:blue')
        
        self.connect(self.slider, SIGNAL("valueChanged(int)"), self._on_value_change)
        self.slider.setRange(-100, 100)
        
        self.value_code = (lambda v: v) if value_code is None else (value_code)
        self.label_code = label_code
        self.value = self.value_code(0)
        

    def _on_value_change(self, value):
        self._value = self.value_code(value)
        self.label.setText(self.label_code(self._value))
        
    def value(self):
        return self._value


class TabMetadata(QWidget):
    def __init__(self, parent, controller):
        super(TabMetadata, self).__init__(parent)
        self.controller = controller
        self.controller.signal.connect('media-opened', self.on_opened)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.browser = QTextBrowser()
        self.browser.setHtml("<h1>Metadata</h1>")
        layout.addWidget(self.browser)
        
        #self.bottom = QWidget()
        
    
    def on_opened(self, *a):
        self.browser.setHtml(self._metadata_to_html(self.controller.get_meta_data()))
    
    def _metadata_to_html(self, md):
        result=['<h1>%s</h1>' % md[0]]
        
        for name, tab in md[1:]:
            result.append('<h2>%s</h2>' % name)
            result.append('<table>')
            
            for row in tab:
                result.append('<tr><td>%s</td><td>%s</td></tr>' % row)
            result.append('</table>')
            
        return '\n'.join(result)


class TabInfo(QWidget):
    def __init__(self, parent, controller):
        super(TabInfo, self).__init__(parent)
        self.controller = controller
        self.controller.signal.connect('media-opened', self.on_opened)
        
        layout = QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml("<h1>Info</h1>")
        #self.browser.document().setDefaultStyleSheet(css)
        layout.addWidget(self.browser)
        
        self.menu = QMenu()
        #self.menu.
        action = self.menu.addAction("Ala ma kota")
        
        self.button = QPushButton(u"Reload")
        self.button.setMenu(self.menu)
        layout.addWidget(self.button)
        
        #self.imdb = imdb_info.IMDbInfo()
        self.imdb = imdb_info.MediaInfo()
    
    def _set_menu(self, items):
        self.menu.clear()
        
        for item in items:
            self.menu.addAction(item)
        
        #self.button.setMenu(self.menu)
    
    def on_opened(self, *a):
        class InfoThread(QThread): 
            def __init__(self, parent):
                QThread.__init__(self, parent)
                self.parent = parent
            
            def run(self):
                logging.debug('player.filename %r' % self.parent.controller.player.filename)
                #self.parent._info_text, self.parent._info_img = imdb_info.IMDbInfo().get_html(self.parent.controller.player.filename)
                self.parent._info = self.parent.imdb.get_info(self.parent.controller.player.filename)
                #self.parent._info = imdb_info.IMDbInfo().get_html(self.parent.controller.player.filename)
        
        self.browser.setHtml('<b>loading...</b>')
        
        self._info_thread =  InfoThread(self)
        self.connect(self._info_thread, SIGNAL("finished()"), self._set_info_text)
        self._info_thread.start()
        
    #def _set_info_text(self):
    #    if self._info_text:
    #        if self._info_img is not None:
    #            img = QImage()
    #            img.loadFromData(self._info_img)
    #            self.browser.document().addResource(
    #                QTextDocument.ImageResource,
    #                QUrl("mem://image"),
    #                QVariant(img)
    #            )
    #        
    #        self.browser.setHtml(self._info_text)
    #    else:
    #        self.browser.setHtml('<b>Not Found</b>')
    
    def _set_info_text(self):
        if self._info:
            import pprint
            #self.browser.setText(pprint.pformat(self._info))
            self._set_menu(self._info['list'])
            html, data = self.imdb.get_html(self._info)
            for d in data:
                img = QImage()
                img.loadFromData(data[d])
                self.browser.document().addResource(
                    QTextDocument.ImageResource,
                    QUrl("mem://" + d),
                    QVariant(img)
                )
            self.browser.setHtml(html)
        else:
            self.browser.setHtml('<b>Not Found</b>')


class TabPlaylist(QWidget):
    def __init__(self, parent, controller):
        super(TabPlaylist, self).__init__(parent)
        self.controller = controller
        
        layout = QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        
        self.menu = QMenuBar()
        layout.addWidget(self.menu)
        
        fileMenu = self.menu.addMenu('File')
        fileMenu.addAction(create_action(self, 'Load playlist', self.on_playlist_load))
        fileMenu.addAction(create_action(self, 'Save playlist', self.on_playlist_save))
        
        addMenu = self.menu.addMenu('Add')
        addMenu.addAction(create_action(self, 'Add file',      self.on_playlist_add_file))
        addMenu.addAction(create_action(self, 'Add directory', self.on_playlist_add_directory))
        addMenu.addAction(create_action(self, 'Add playlist',  self.on_playlist_add_playlist))
     
        sortMenu = self.menu.addMenu('Sort')
        sortMenu.addAction(create_action(self, 'By Name',      partial(self.on_playlist_sort, 'name')))
        sortMenu.addAction(create_action(self, 'By File Name', partial(self.on_playlist_sort, 'filename')))
        sortMenu.addAction(create_action(self, 'Random',       partial(self.on_playlist_sort, 'random')))
        sortMenu.addSeparator()
        sortMenu.addAction(create_action(self, 'Reverse',      partial(self.on_playlist_sort, 'reverse')))
        
        modeMenu = self.menu.addMenu('Mode')
        modeMenu.addAction(create_action(self, 'Default',      partial(self.on_playlist_mode, 'default')))
        modeMenu.addAction(create_action(self, 'Shuffle',      partial(self.on_playlist_mode, 'shuffle')))
        modeMenu.addAction(create_action(self, 'Repeat',       partial(self.on_playlist_mode, 'repeat')))
        modeMenu.addAction(create_action(self, 'Repeat one',   partial(self.on_playlist_mode, 'repeat-one')))
        
        
        
        self.list_model = PlaylistModel(controller)
        
        self.table = QTableView()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setGridStyle(Qt.NoPen)
        self.table.connect(self, SIGNAL("doubleClicked(QModelIndex)"), self.list_model.signal_doubleClicked)
        self.table.setModel(self.list_model)
        layout.addWidget(self.table)
        
        
        self.controller.signal.connect('playlist', self.playlist_update)
        
        
    def playlist_update(self, *a):
        self.table.setModel(None)
        self.table.setModel(self.list_model)


    def on_playlist_load(self):
        pass
    
    def on_playlist_save(self):
        def save_dialog(caption, dir, formats):
            build_exts = lambda exts: ' '.join("*.%s" % i.lower() for i in exts)
            filters = ["%s (%s)" % (i[0], build_exts(i[1])) for i in formats]
                
            dialog = QFileDialog(self, caption, dir or ".", ';;'.join(filters))
            
            if dialog.exec_():
                filename = unicode(dialog.selectedFiles()[0])
                
                filter = dialog.selectedFilter()
                filter_index = filters.index(filter)
                
                selected_format = formats[filter_index]
                if not filename.endswith(tuple(['.' + i for i in selected_format[1]])):
                    filename += '.' + selected_format[1][0]
                    format = selected_format[1][0]
                else:
                    format = filename.rsplit('.', 1)[-1]
                
                #print filename, filter, filter_index
                return filename, format
            else:
                return None, None
        
        formats = self.controller.playlist.playlist_formats()
        
        filename, format = save_dialog("Save playlist", '.', formats)
        self.controller.playlist.save(filename, format)
        
    def on_playlist_add_file(self):
        pass
    
    def on_playlist_add_directory(self):
        pass
    
    def on_playlist_add_playlist(self):
        pass
    
    def on_playlist_sort(self, what):
        self.controller.playlist.sort(what)
        self.playlist_update()
        
    def on_playlist_mode(self, what):
        self.controller.playlist.mode = what
        #self.playlist_update()
    
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


class TabSubtitles(QWidget):
    def __init__(self, parent, controller):
        super(TabSubtitles, self).__init__(parent)
        self.controller = controller


class TabSettings(QWidget):
    def __init__(self, parent, controller):
        super(TabSettings, self).__init__(parent)
        self.controller = controller
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(NiceSlider(lambda v: 'Volume %s' % v, None, self))
        layout.addWidget(NiceSlider(lambda v: 'Balance %s' % v, None, self))
        layout.addWidget(NiceSlider(lambda v: 'Bass %s' % v, lambda v: v**3, self))
        layout.addWidget(QWidget(self))


class GuiSidebar(QTabWidget):
    def __init__(self, parent, controller):
        QTabWidget.__init__(self, parent)
        self.controller = controller
        
        css = """
        table {border-color: black; border-style: solid;}
        
        h1 {color: red; background-color:#ddd; margin-bottom:0px;}
        h2 {color: blue; background-color:#ddd; margin-bottom:0px;}
        """
        
        self.tab_info = TabInfo(self, controller)
        self.tab_meta = TabMetadata(self, controller)
        self.tab_list = TabPlaylist(self, controller)
        self.tab_subs = TabSubtitles(self, controller)
        self.tab_sett = TabSettings(self, controller)
        
        self.addTab(self.tab_info, "Info")
        self.addTab(self.tab_meta, "Meta")
        self.addTab(self.tab_list, "List")
        self.addTab(self.tab_subs, "Subs")
        self.addTab(self.tab_sett, "Sett")
        self.setFixedWidth(250)

