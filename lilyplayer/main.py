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
import os
import os.path
import time
import random
import platform
import logging


from lilyplayer.gui.qt4 import GuiMain
from lilyplayer.utils.play_time import Time
from lilyplayer.player.player import Player
from lilyplayer.utils.arguments import PrefixArg, FloatArg, IntArg, TimeArg, StrArg, EnumArg, parse_arguments, args
from lilyplayer.playlist.playlist import Playlist
from lilyplayer.playlist.playlist import PlaylistEntry
from lilyplayer.subtitles.subtitles import Subtitles

import lilyplayer.utils.compose_thumbs as compose_thumbs
import lilyplayer.settings
import lilyplayer.utils.utils as utils

__version__ = (0, 3, 1)
__author__ = 'Krzysztof Kosyl'
_copyright__ = 'GNU General Public License'


def prefix_value_change(prop, prefix, value):
    if prefix == '+':
        return prop + value
    elif prefix == '-':
        return prop - value
    elif prefix == '*':
        return prop * value
    elif prefix == '/':
        return prop / value
    else:
        return value


class Signal(object):
    def __init__(self):
        self.signals = {}
        
    def emit(self, name, *params):
        print '-' * 100
        print 'Signals:', self.signals
        print '-' * 100
        parts = name.split('-')
        for i in xrange(len(parts), 0, -1):
            nm = '-'.join(parts[:i])
            print nm
            for fun, args in self.signals.get(nm, []):
                print 'send %r to %r' % (nm, fun), args, params, args + params
                fun(args, *list(args + params))
    
    def connect(self, name, fun, *args):
        if name in self.signals:
            self.signals[name].append((fun, args))
        else:
            self.signals[name] = [(fun, args)]
    
    def disconnect(self, name, fun):
        pass


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

class Controler(object):
    arguments_table = []
    
    main_menu = MenuItem('', submenu=[
        MenuItem('File', submenu=[
            MenuItem('Open', cmd='opendlg'),
            MenuItem('Close', cmd='close'),
            MenuItem(''),
            MenuItem('Exit', cmd='exit'),
        ]),
        MenuItem('View', submenu=[
            MenuItem('Sidebar', cmd='view-sidebar toggle'),
        ]),
        
        MenuItem('Playback', submenu=[
            MenuItem('Play', cmd='play'),
            MenuItem('Pause', cmd='pause'),
            MenuItem('Stop', cmd='stop'),
            MenuItem(''),
            MenuItem('Goto', cmd='gotodlg'),
            MenuItem(''),
            MenuItem('Speed', submenu=[
                MenuItem('25%',  cmd='speed 25%'),
                MenuItem('50%',  cmd='speed 50%'),
                MenuItem('100%', cmd='speed 100%'),
                MenuItem('200%', cmd='speed 25%'),
                MenuItem('400%', cmd='speed 25%'),
            ]),
        ]),
        MenuItem('Video', submenu=[
            MenuItem('Video scale', submenu=[
                MenuItem('50%',  cmd='video-scale 50%'),
                MenuItem('75%',  cmd='video-scale 75%'),
                MenuItem('100%', cmd='video-scale 100%'),
                MenuItem('150%', cmd='video-scale 150%'),
                MenuItem('200%', cmd='video-scale 200%'),
                #MenuItem('250%', cmd='video-scale 250%'),
                MenuItem('300%', cmd='video-scale 300%'),
                #MenuItem('350%', cmd='video-scale 350%'),
                MenuItem('400%', cmd='video-scale 400%'),
                MenuItem(''),
                MenuItem('Enter...', cmd='video-scale-dlg'),
            ]),
        ]),
        MenuItem('Audio', submenu=[
            MenuItem('Mute', cmd='mute'),
            MenuItem('Volume Down', cmd='volume -10%'),
            MenuItem('Volume Up', cmd='volume +10%'),
        ]),
        MenuItem('Tools', submenu=[
            MenuItem('Snapshot', cmd='snap'),
            MenuItem('Thumbinals', cmd='thumbdlg'),
        ]),
        MenuItem('Help', submenu=[
            MenuItem('About', cmd='about'),
        ]),
    ])

    def __init__(self):
        self.playlist = Playlist(sys.argv[1:])
        self.subtitles = Subtitles()
        self.signal = Signal()
        self.gui = GuiMain(self)
        self.gui.update_menu(self.main_menu)
        self.player = Player.create('gstreamer', self.gui, self.gui.movie_window.winId())
        settings.get_path('data', 'mainicon.png')
    
    def exec_(self):
        self.gui.exec_()
    
    def dispatch(self, args):
        if args is not None:
            parsed = parse_arguments(self.arguments_table, args)
            parsed[0](*([self] + parsed[1:]))


    def keyboard_shortcut(self, keys):
        shortcuts = settings.get('shortcut')
        if keys in shortcuts:
            msg = shortcuts[keys]
            self.dispatch(msg)

    def on_start(self):
        #self.playlist = Playlist(sys.argv[1:])
        
        self.open_item(self.playlist.next())
        

    def on_timer(self):
        if self.player.state == 'finish':
            self.playlist_next()
            #next = self.playlist.next()
            #self.open_item(next)
        #self.slider.setValue(int(self.player.position_fraction * 1000))
        self.gui.controls._redraw(self)



    def open_dlg(self):
        filename = self.gui.do_file_dialog('Open file', mode='open', path=None, filter=None)
        print filename
        if filename:
            self.open(filename)

    def open(self, filename):
        if filename.startswith('file://'):
            filename = filename[7:]
        item = self.playlist.append_and_goto(filename)
        self.open_item(item)
        self.signal.emit('playlist-append')
        print 'controler id', id(self.playlist)

    def open_item(self, item):
        if item:
            self.player.stop()
            
            self.gui.window.setWindowTitle("%s - Lily Player"  % item.name)
            logging.info("Media file opening: %r" % item.filename)
            self.player.open(item.filename)
            logging.info("Media file opened")
            self.video_scale(1.0)
            if False:
                try:
                    subname = item.filename.rsplit('.', 1)[0] + '.txt'
                    self.subtitles.load(subname, encoding='cp1250')
                    self.subtitles.adjust_fps(self.player.video.framerate)
                    self.subtitles.adjust_time(perchar=Time(s=0.01), minimum=Time(s=2))
                except Exception, e:
                    print e
                
            self.player.play()
            self.signal.emit('media-opened')
            self.info_media_filename = item.filename
        else:
            self.gui.window.setWindowTitle("Lily Player")
            self.player.stop()



   
    def play(self):
        self.player.play()
    def pause(self):
        self.player.pause()
    def stop(self):
        self.player.stop()
    def toggle(self):
        self.player.toggle()
        
    def get_state(self):
        return self.player.state
    def set_state(self, value):
        self.player.state = value
        
    def get_mute(self):
        return self.player.mute
    def set_mute(self, value=None):
        self.player.mute = value
        
    def get_volume(self):
        return self.player.volume
    def set_volume(self, value):
        self.player.volume = value
        
    def get_position(self):
        return self.player.position
    def set_position(self, value):
        self.player.position = value

    def get_position_fraction(self):
        return self.player.position_fraction
    def set_position_fraction(self, value):
        self.player.position_fraction = value
        
    def get_duration(self):
        return self.player.duration



    def get_current_subtitle(self):
        verses = self.subtitles.at(self.player.position)
        if verses:
            print verses
        text = (u'<br/>'.join(i.text for i in verses)).replace(u'\n', u'<br/>')
        return text.encode('ascii', 'xmlcharrefreplace')

    def goto_dlg(self):
        time = self.gui.do_input_dlg('Run command', 'Enter command', str(self.player.position))
        try:
            self.player.position = Time.parse(time)
        except ValueError:
            pass

    def about(self):
        libs = [ 
            ('Python', platform.python_version()),
            ('System', platform.system() + " " + platform.release()),
        ]
        libs.extend(self.player.versions())
        self.gui.do_about(authors=[__author__], version=__version__, libs=libs)

    def exit(self):
        self.player.close()
        exit()

    def get_fullscreen(self):
        return self.gui.do_get_fullscreen()
    
    def set_fullscreen(self, value=None):
        if value is None:
            value = not self.gui.do_get_fullscreen()
        
        self.gui.do_set_fullscreen(value)
        
    def view_sidebar(self, value=None):
        if value is None:
            value = not self.gui.do_get_view_sidebar()
        
        self.gui.do_set_view_sidebar(value)
        

    def playlist_goto(self, index):
        self.open_item(self.playlist.goto(index))
        self.signal.emit('playlist-goto')
    
    def playlist_next(self):
        self.open_item(self.playlist.next())
        self.signal.emit('playlist-next')

    def get_meta_data(self):
        structs = [
            ('Video', self.player.video),
            ('Audio', self.player.audio),
            ('Other', self.player.metadata)
        ]

        meta = dict(self.player.metadata)
        
        
        result=['Metadata']
        for name, struct in structs:
            tab = []
            for i in struct:
                tab.append((i, struct[i]))
            result.append((name, tab))
        
        meta = dict(self.player.metadata)
            
        tmp = []
        if 'video-width' in meta:
            tmp.append(('Width', meta['video-width']))
        if 'video-height' in meta:
            tmp.append(('Height', meta['video-height']))
        if 'video-width' in meta and 'video-height' in meta:
            w = meta['video-width']
            h = meta['video-height']
            rw, rh = utils.reduce_fraction(w, h)
            tmp.append(('Ratio', '%d:%d (%.2f:1)' % (rw, rh, float(rw) / rh)))
            tmp.append(('MegaPixels', '%.2f' % (w * h / 1000000.0)))
        result.append(('Video', tmp))    
        
            

        return result

    def thumbinals(self, cols, rows, size, margin):
        count = rows * cols
        
        saved_pos = self.player.position_fraction
        saved_state = self.player.state
        self.player.pause()
        
        result = []
        
        for i in xrange(1, count + 1):
            last_pos = self.player.position_fraction
            seek_pos = i * (1.0 / (count + 1))
            self.player.position_fraction = seek_pos

            format, data = self.player.snapshot()
            label = str(self.player.position)
            result.append((data, label))

            #filename = os.path.expanduser('~/thumb_%.4d.%s' % (i, format))
            #fo = open(filename, 'wb')
            #fo.write(data)
            #fo.close()

        compose_thumbs.compose(
                result, 
                outfile=os.path.join(os.path.expanduser('~'), 'thumb.png'),
                size=size, cols=cols, border=margin,
        )
        
        self.player.position_fraction = saved_pos
        self.player.state = saved_state


    def thumbinals_dialog(self):
        defaults = utils.Struct(
            cols=settings.get('gui.thumb.cols'),
            rows=settings.get('gui.thumb.rows'),
            size=settings.get('gui.thumb.size'),
            margin=settings.get('gui.thumb.margin')
        )
        struct = self.gui.do_thumbinals_dialog(defaults)
        if struct is not None:
            s = struct
            self.thumbinals(s.cols, s.rows, s.size, s.margin)
            
    def video_scale(self, scale=1.0):
        if self.get_fullscreen():
            logging.info("Try 'video_scale' - in fullscreen mode")
            return
        if self.player.video is not None and 'width' in self.player.video and 'height' in self.player.video:
            w = scale * self.player.video.width
            h = scale * self.player.video.height
            self.gui.do_resize_video_window(w, h)
        else:
            logging.warn("Try 'video_scale' - video size unknown")
            
    @args(arguments_table, 'theme', StrArg())
    def cmd_theme(self, name):
        settings.set('gui.theme', name)
        self.signal.emit('theme')
            
    @args(arguments_table, 'video-scale-dlg')
    def cmd_video_scale_dlg(self):
        result = self.gui.do_input_dlg('Video scale', 'Enter scale')
        self.dispatch('video-scale ' + result)
    
    @args(arguments_table, 'video-scale', FloatArg(0.2, 5.0))
    def cmd_video_scale(self, scale):
        self.video_scale(scale)
    
    @args(arguments_table, 'thumbdlg')
    def cmd_thumb_dlg(self):
        self.thumbinals_dialog()
    
    @args(arguments_table, 'exit')
    def cmd_exit(self):
        self.exit()
    
    @args(arguments_table, 'about')
    def cmd_about(self):
        self.about()
    
    @args(arguments_table, 'cmddlg')
    def cmd_cmddlg(self):
        cmd = self.gui.do_input_dlg('Run command', 'Enter command')
        self.dispatch(cmd)
    
    @args(arguments_table, 'gotodlg')
    def cmd_gotodlg(self):
        self.goto_dlg()
    
    @args(arguments_table, 'open', StrArg())
    def cmd_open(self, url):
        self.open(url)
    
    @args(arguments_table, 'opendlg')
    def cmd_opendlg(self):
        self.open_dlg()
    
    @args(arguments_table, 'close')
    def cmd_close(self):
        self.player.close()
    
    @args(arguments_table, 'speed', PrefixArg(['+', '-', '=', '']), FloatArg(0.25, 4.0))
    def cmd_speed(self, prefix, value):
        self.player.speed = prefix_value_change(self.player.speed, prefix, value)
    
    @args(arguments_table, 'goto', PrefixArg(['+', '-', '=', '']), FloatArg(0.0, 1.0))
    def cmd_goto_pos(self, prefix, value):
        self.player.position_fraction = prefix_value_change(self.player.position_fraction, prefix, value)
    
    @args(arguments_table, 'goto', PrefixArg(['+', '-', '=', '']), TimeArg())
    def cmd_goto_time(self, prefix, value):
        self.player.position = prefix_value_change(self.player.position, prefix, value)
    
    @args(arguments_table, 'volume', PrefixArg(['+', '-', '=', '']), FloatArg(0.0, 1.0))
    def cmd_volume(self, prefix, value):
        self.player.volume = prefix_value_change(self.player.volume, prefix, value)
    
    @args(arguments_table, 'mute')
    def cmd_mute(self):
        self.player.mute = None
    
    @args(arguments_table, 'snap')
    def cmd_snap(self):
        format, data = self.player.snapshot()
        filename = os.path.expanduser('~/lily_%s.%s' % (time.strftime('%Y-%m-%d_%H:%M:%S'), format))
        fo = open(filename, 'wb')
        fo.write(data)
        fo.close()
    
    @args(arguments_table, 'thumb', IntArg(1, 10), IntArg(1, 100))
    def cmd_thumb(self, rows, cols):
        self.thumbinals(rows, cols, 200, 10)
    
    @args(arguments_table, 'play')
    def cmd_play(self):
        self.player.play()
    
    @args(arguments_table, 'pause')
    def cmd_pause(self):
        self.player.pause()
    
    @args(arguments_table, 'stop')
    def cmd_stop(self):
        self.player.stop()
    
    @args(arguments_table, 'toggle')
    def cmd_toggle(self):
        self.player.toggle()
    
    @args(arguments_table, 'fullscreen', EnumArg({'on': True, 'off': False}))
    def cmd_fullscreen_enum(self, enum):
        self.set_fullscreen(enum)
    
    @args(arguments_table, 'fullscreen')
    def cmd_fullscreen(self):
        self.set_fullscreen(None)
    
    @args(arguments_table, 'playlist-next')
    def cmd_playlist_next(self):
        print 'playlist next'
        self.open_item(self.playlist.next())
    
    @args(arguments_table, 'playlist-mode', EnumArg(['repeat-one', 'repeat', 'shuffle', 'default']))
    def cmd_playlist_mode(self, mode):
        """ Changes playlist mode to specified """
        self.playlist.mode = mode
    
    @args(arguments_table, 'playlist-goto', IntArg(0))
    def cmd_playlist_goto(self, index):
        """ Changes playlist current item do specified """
        self.playlist_goto(index)
        
    @args(arguments_table, 'view-sidebar', EnumArg({'on': True, 'off': False, 'toggle': None}))
    def cmd_view_sidebar(self, enum):
        self.view_sidebar(enum)

def main():
    logging.basicConfig(
        level=logging.DEBUG, #logging.INFO,
        format='%(asctime)s  %(levelname)-8s  %(module)-12s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    
    controler = Controler() 
    controler.exec_()

if __name__ == '__main__':
    main()
