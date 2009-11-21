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


import time
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import logging


from PyQt4.QtCore import *
from PyQt4.QtGui import *


class GuiMarkupWindow(QDialog):
    class MarkupHandler(ContentHandler):
        def __init__(self):
            ContentHandler.__init__(self)
            self.format = [dict(color="#ffffff", bold=False, italic=False, underline=False, overline=False)]
            self.data = [[]]
            
        def startElement(self, name, attrs):
            
            def set_dict(dic, key, val):
                if val:
                    dic[key] = val
                return True
            
            if name == 'br':
                self.data.append([])
            else:
                new_dict = dict(self.format[-1])
    
                code = {
                    'i': lambda d: set_dict(d, 'italic', True),
                    'b': lambda d: set_dict(d, 'bold', True),
                    'u': lambda d: set_dict(d, 'underline', True),
                    'o': lambda d: set_dict(d, 'overline', True),
                    'font': lambda d: set_dict(d, 'color', attrs.get('color', None)) and set_dict(d, 'size', int(attrs.get('size', '0'))),
                }
                
                code.get(name, lambda d: True)(new_dict)
                
                self.format.append(new_dict)
        def endElement(self,name):
            if name == 'br':
                return
            self.format.pop()
    
        def characters(self, value): 
            self.data[-1].append((self.format[-1], value))
    
        
        @staticmethod
        def parse(text):
            format = GuiMarkupWindow.MarkupHandler()
            
            saxparser = make_parser()
            saxparser.setContentHandler(format)
            saxparser.feed(u'<span>' + unicode(text) + u'</span>')
            
            return format.data

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        #self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAutoFillBackground(True)
        #self.setWindowIconText("X")
        #self.setWindowTitle(" ")
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft);
        
        self.render('')
        
        self.old_text = None
        self.style = {}
    
    def render(self, text, style={}):
        """
            Params:
                text: text to render (containing markup)
                style: CSS like style, posible keys: {font-size, font-color, border-width, border-color, background-color}
        """
        
        if not text:
            self.resize(QSize(0, 0))
            return
        
        base_margin = 6
        
        base_font = QFont()
        base_font.setPixelSize(int(style.get('font-size', '24')),)
        
        base_metrics = QFontMetrics(base_font)
        base_height = base_metrics.height()
        base_ascent = base_metrics.ascent()
        
        spec = [[]] #format: (x, y, font, color, text)
        widths = []
        
        data = GuiMarkupWindow.MarkupHandler.parse(text)
        for line_num, line in enumerate(data):
            line_width = 0
            for format, text in line:
                script_y = 0
                
                font = QFont(base_font)
                font.setItalic(format['italic'])
                font.setBold(format['bold'])
                font.setUnderline(format['underline'])
                font.setOverline(format['overline'])
                if 'size' in format:
                    font.setPixelSize(format['size'])
                
                fm = QFontMetrics(font)
                text_width = fm.width(text)
                
                spec[-1].append([
                        line_width, 
                        line_num * base_height + base_ascent + script_y,
                        font, format['color'], text
                ])
                
                line_width += text_width

            spec.append([])
            widths.append(line_width)

        if spec[-1] == []:
            spec = spec[:-1]

        max_width = max(widths) + 2 * base_margin
        
        for line_width, line in zip(widths, spec):
            offset = (max_width - line_width) / 2
            for s in line:
                s[0] += offset
        
        
        pixmap = QPixmap(max_width, base_height * len(spec))
        pixmap.fill(QColor(0, 0, 0, 0))
        
        painter = QPainter()
        painter.begin(pixmap)
        
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        
        painter.setBrush(QBrush(QColor(style.get('font-color', '#ffffff'))))
        
        if 'border-width' in style:
            painter.setPen(QPen(
                QBrush(QColor(style.get('border-color', '#444444'))),
                int(style.get('border-width', '0')),
                Qt.SolidLine, Qt.RoundCap
            ))
        else:
            painter.setPen(Qt.NoPen)
        
        if 'background-color' in style:
            for i, w in enumerate(widths):
                painter.fillRect(
                    QRect(
                        (max_width - w) / 2 - base_margin, base_height * i, 
                        w + 2 * base_margin, base_height
                    ), 
                    QBrush(QColor(style['background-color']))
                )
        
        aspec = sum(spec, [])
        
        for x, y, font, color, text in aspec:
            path = QPainterPath()
            path.addText(QPointF(x, y), font, text)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawPath(path)
        
        painter.end()

        self.label.clear()
        self.resize(pixmap.size())
        self.label.resize(pixmap.size())
        self.setMask(pixmap.mask())
        
        self.label.setPixmap(pixmap)

    def set_style(self, style):
        self.style = style
        self.render(self.old_text)

    def set_text(self, text):
        if self.old_text != text:
            self.old_text = text
            self.render(self.old_text, self.style)
         
    def paintEvent(self,event):
        pass
        self.setAttribute(Qt.WA_NoSystemBackground)

if __name__ == "__main__":
    app = QApplication([])
    markup_window = GuiMarkupWindow()
    markup_window.show()
    markup_window.render('%s<br/><font color="#888888"><o>i</o> <b>jest</b> <u>ok</u></font><br/><font color="#f00">128</font><font size="20">end...</font>' % time.strftime('%H:%M:%S'), {'background-color':'#111111', 'border-width':'0'})
    app.exec_()