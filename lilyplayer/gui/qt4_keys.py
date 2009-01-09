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
