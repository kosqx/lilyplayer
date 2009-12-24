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


import lilyplayer.subtitle_source as subtitle_source


class SubtitlesModel(QAbstractTableModel):

    def __init__(self, controller):
        super(SubtitlesModel, self).__init__()
        self.controller = controller
        
        self.sources = []
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        column = index.column()
        
        if role == Qt.DisplayRole and row < len(self.sources) and column < 3:
            return QVariant(QString(self.sources[row][column] or ""))
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(['Src', 'Lang', 'Name'][section])
       
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(int(section + 1))
        return QVariant()
    
    def rowCount(self, index=QModelIndex()):
        return len(self.sources)
    
    def columnCount(self, index=QModelIndex()):
        return 3
    
    def set_sources(self, sources):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.sources = sources or []
        self.emit(SIGNAL("layoutChanged()"))
    
    def get_subtitles(self, index):
        return subtitle_source.get_subtitles(self.sources[index])
    

class TabSubtitles(QWidget):
    def __init__(self, parent, controller):
        super(TabSubtitles, self).__init__(parent)
        self.controller = controller
        self.controller.signal.connect('media-opened', self.on_opened)
        
        layout = QVBoxLayout()
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self._sources = None
        self.list_model = SubtitlesModel(controller)
        self.table = QTableView(parent)
        
        self.table.setModel(self.list_model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setShowGrid(False)
        
        layout.addWidget(self.table)
        
        self.connect(self.table, SIGNAL("doubleClicked(QModelIndex)"), self.on_double_clicked)
    
    def on_opened(self, *a):
        class InfoThread(QThread): 
            def __init__(self, parent):
                QThread.__init__(self, parent)
                self.parent = parent
            
            def run(self):
                self.parent._sources = subtitle_source.get_list(self.parent.controller.player.filename)
        
        self._info_thread =  InfoThread(self)
        self.connect(self._info_thread, SIGNAL("finished()"), self._set_list)
        self._info_thread.start()
        
    def _set_list(self):
        print '+' * 200
        print [s[:3] for s in self._sources]
        
        self.list_model.set_sources(self._sources)
    
    def on_double_clicked(self, index):
        sub = self.list_model.get_subtitles(index.row())
        self.controller.set_subtitles(sub)
        #sub = self.list_model.get_subtitles(index.row())
        #print sub
        #self.controller.subtitles = sub

