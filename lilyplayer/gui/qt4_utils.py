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


from PyQt4.QtCore import *
from PyQt4.QtGui import *



if sys.version_info[:2] < (2, 5):
    def partial(func, arg):
        def callme():
            return func(arg)
        return callme
else:
    from functools import partial


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


class FileDialog:
	"""
		Example:
		formats = [
			('ASDF file', ['asdf', 'asd']),
			(None, ['jpeg', 'jpg']),
			('Any', None),
		]
	"""
	def __init__(self, parent, formats):
		def build_filters(formats):
			filters = []
			for format in formats:
				assert format[0] is not None or format[1] is not None
				if format[0] is not None:
					name = format[0]
				else:
					name = "%s file" % format[1][0].upper()
				exts = ' '.join("*.%s" % i.lower() for i in format[1])
				if exts:
					exts  = " (" + exts + ")"
				filters.append(name + exts)
			return filters
		
		def build_exts(formats):
			exts = []
			for f in formats:
				if f[1]:
					exts.extend(f[1])
			return exts
		
		self._parent  = parent
		self._formats = formats
		self._filters = build_filters(formats)
		self._exts    = build_exts(formats)
		
	def setFilter(self, *a):
		print unicode(a[0])
		
	def showSave(self, dir='.'):
		dialog = QFileDialog(self._parent, u"Save file", dir or ".", ';;'.join(self._filters))
		dialog.setFileMode(QFileDialog.AnyFile)
		dialog.setAcceptMode(QFileDialog.AcceptSave)
		#dialog.connect(dialog, SIGNAL("filterSelected(QString)"), self.setFilter)
		if dialog.exec_():
			self.filename = unicode(dialog.selectedFiles()[0])
			filter = dialog.selectedFilter()
			filter_index = self._filters.index(filter)
			
			format = self._formats[filter_index]
			if not self.filename.endswith(tuple('.' + i for i in format[1])):
				self.filename += '.' + format[1][0]
				self.format = format[1][0]
			else:
				self.format = self.filename.rsplit('.', 1)[-1]
			
			if len(format) >= 3:
				self.selection = format[2]
			else:
				self.selection = format[1][0]
		else:
			return False
		
	

