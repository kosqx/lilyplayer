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


class MenuItem(object):
    @staticmethod
    def text_to_name(text):
        result = []
        for c in text.lower():
            if ('a' <= c <= 'z') or ('0' <= c <= '9'):
                result.append(c)
        return ''.join(result)
    
    def __init__(self, text, name=None, cmd=None, submenu=None):
        self.text = text
        if name:
            self.name = name
        else:
            self.name = MenuItem.text_to_name(text)
        
        self.cmd     = cmd
        self.submenu = submenu
        
    def is_item(self):
        return self.cmd is not None
    
    def is_submenu(self):
        return self.submenu is not None
    
    def is_separator(self):
        return (self.cmd is None) and (self.submenu is None)
    
    def by_name(self, name):
        result = []
        
        if self.submenu:
            for item in self.submenu:
                if name == item.name or (name.endswith(':') and item.name.startswith(name)):
                    result.append(item)
        
        return result


def create_action(this, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
	action = QAction(text, this)
	if icon is not None:
		action.setIcon(QIcon(":/%s.png" % icon))
	if shortcut is not None:
		action.setShortcut(shortcut)
	if tip is not None:
		action.setToolTip(tip)
		action.setStatusTip(tip)
	if slot is not None:
		action.connect(action, SIGNAL(signal), slot)
	if checkable:
		action.setCheckable(True)
	return action

