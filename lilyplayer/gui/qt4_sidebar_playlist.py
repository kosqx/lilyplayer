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

from lilyplayer.gui.qt4_utils import create_action, partial

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
        #logging.debug('playlist length: %r' % len(self.playlist))
        return len(self.playlist)
    
    def columnCount(self, index=QModelIndex()):
        return 2


class PlaylistTableView(QTableView):
    def __init__(self, parent, controller):
        super(PlaylistTableView, self).__init__(parent)
        self.controller = controller
        
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()
        #else:
        #    event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        #else:
        #    event.ignore()

    def dropEvent(self, event):
        print 'dropEvent'
        if event.mimeData().hasUrls():
            urls = [unicode(i.path()) for i in event.mimeData().urls()]
            event.acceptProposedAction()
            #event.setDropAction(Qt.CopyAction)
            logging.debug('sidebar dropEvent urls: %r' % urls)
            
            index = self.indexAt(event.pos())
            if index.isValid():
                row = index.row()
            else:
                row = None
            # TODO: append all
            logging.debug('sidebar dropEvent row: %r' % row)
            self.controller.playlist_extend(urls, row)
        #else:
        #    event.ignore()

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
        
        #self.table = QTableView()
        self.table = PlaylistTableView(self, self.controller)
        self.table.setModel(self.list_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setGridStyle(Qt.NoPen)
        #self.table.setAutoUpdate(True)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.connect(self.table, SIGNAL("doubleClicked(QModelIndex)"), self.on_double_clicked)
        #self.connect(self.table, SIGNAL("clicked(QModelIndex)"), self.on_double_clicked)
        #self.connect(self.table, SIGNAL('itemPressed(QListWidgetItem*)'), self.on_double_clicked)
        
        
        layout.addWidget(self.table)
        
        #self.setAcceptDrops(True)
        self.controller.signal.connect('playlist', self.playlist_update)
        
    #def dragEnterEvent(self, event):
    #    if event.mimeData().hasUrls():
    #        event.acceptProposedAction()
    #    else:
    #        event.ignore()
    #
    #def dropEvent(self, event):
    #    if event.mimeData().hasUrls():
    #        urls = [unicode(i.path()) for i in event.mimeData().urls()]
    #        event.acceptProposedAction()
    #        event.setDropAction(Qt.CopyAction)
    #        logging.debug('sidebar dropEvent urls: %r' % urls)
    #        
    #        index = self.table.indexAt(event.pos())
    #        if index.isValid():
    #            row = index.row()
    #        else:
    #            row = None
    #        # TODO: append all
    #        logging.debug('sidebar dropEvent row: %r' % row)
    #        self.controller.playlist_extend(urls, row)
    #    else:
    #        event.ignore()
        
    def on_double_clicked(self, index):
        self.controller.playlist_goto(index.row())
        
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


