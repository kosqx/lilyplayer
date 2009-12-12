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
from lilyplayer.gui.qt4_sidebar_playlist import TabPlaylist




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
        layout.setMargin(0)
        layout.setSpacing(0)
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
        self._info = None
    
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
                #self.parent._info = imdb_info.IMDbInfo().get_html(self.parent.controller.player.filename)
                
                
                #self.parent._info = self.parent.imdb.get_info(self.parent.controller.player.filename)
        
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

