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

import time

import pygst
pygst.require("0.10")
import gst
import gobject

from PyQt4.QtCore import QThread

from utils import clamp
from play_time import Time

import threading


class Player(object):
    @staticmethod
    def create(backend, window, xid):
        if backend == 'gstreamer':
            return GStreamerPlayer(window, xid)
    
    def __init__(self, window, xid):
        self._mute_volume = None
        pass
    
    def open(self, filename):
        self._do_open(filename)
    
    def close(self):
        self._do_close()
        
    def snapshot(self):
        return self._do_snapshot()

        
    def play(self):
        self._do_set_state("play")
    
    def pause(self):
        self._do_set_state("pause")
     
    def toggle(self):
        state_change = {
            'play':   'pause',
            'pause':  'play',
            'stop':   'play',
            'finish': 'play',
        }
        
        old_state = self._do_get_state()
        if old_state in state_change:
            self._do_set_state(state_change[old_state])
     
    def stop(self):
        self._do_set_state("stop")
    
    def get_state(self):
        return self._do_get_state()
    
    def set_state(self, state):
        self._do_set_state(state)
        
    def get_position(self):
        return Time.from_seconds(self._pos(), 9)

    def set_position(self, time):
        self._seek(time.to_seconds(9))

    def get_position_fraction(self):
        dur = self._dur()
        if dur == 0:
            return 0.0
        pos = self._pos()
        return float(pos) / dur
    
    def set_position_fraction(self, time):
        dur = self._dur()
        if dur == 0:
            return
        pos = long(time * dur)
        self._seek(pos)

    def get_duration(self):
        return Time.from_seconds(self._dur(), 9)
    
    def get_speed(self):
        return self._do_get_speed()

    def set_speed(self, speed):
        #speed = clamp(speed, 0.01, 1000.0)
        self._do_set_speed(speed)

    def get_volume(self):
        return self._do_get_volume()

    def set_volume(self, volume):
        self._do_set_volume(volume)
        self._mute_volume = None
        
    def get_mute(self):
        return self._mute_volume is not None

    def set_mute(self, value):
        if value is None:
            value = self._mute_volume is None
        
        if value:
            self._mute_volume = self._do_get_volume()
            self._do_set_volume(0.0)
        else:
            if self._mute_volume is not None:
                self._do_set_volume(self._mute_volume)
            self._mute_volume = None

    # properties
    state             = property(get_state,             set_state)
    position          = property(get_position,          set_position)
    position_fraction = property(get_position_fraction, set_position_fraction)
    duration          = property(get_duration)
    speed             = property(get_speed,             set_speed)
    volume            = property(get_volume,            set_volume)
    mute              = property(get_mute,              set_mute)



class GStreamerPlayer(Player):

    class SignalThread(QThread): 
        def __init__(self, window, player):
            QThread.__init__(self, window)
            self.player = player
            
        def run(self): 
            gobject.threads_init() 
            bus = self.player._player.get_bus() 
            bus.add_signal_watch()
            bus.enable_sync_message_emission() 
            bus.connect('message', self.on_message) 
            bus.connect('sync-message::element', self.on_sync_message)
            
            self.player._bus = bus
            
        def on_message(self, bus, message): 
            self.player._cb_message(bus, message)

        def on_sync_message(self, bus, message): 
            self.player._cb_sync_message(bus, message)

    class SnapshotPipeline:
        def __init__(self):
            pipeline = ' ! '.join([
                'fakesrc name=src',
                'queue name=queue',
                'videoscale',
                'ffmpegcolorspace',
                'video/x-raw-rgb',
                'pngenc',
                'fakesink name=sink signal-handoffs=true'
            ])

            self.pipeline = gst.parse_launch(pipeline)
            
            self.queue = self.pipeline.get_by_name('queue')
            self.sink  = self.pipeline.get_by_name('sink')
    
            self.sink.connect('handoff', self.cb_snapshot)
            self.pipeline.set_state(gst.STATE_PLAYING)
        
        def cb_snapshot(self, element, buffer, pad):
            self.buffer = buffer
            return True
        
        def snapshot(self, frame):
            self.buffer = None
    
            # Push the frame into the conversion pipeline
            self.queue.get_pad('src').push(frame)
    
            while self.buffer is None:
                pass
            
            return self.buffer.copy()

    def __init__(self, window, xid = None):
        super(GStreamerPlayer, self).__init__(window, xid)
        # debug_threshold in [0, 1, 2, 3, 4, 5]
        #print 'old debug level', gst.debug_get_default_threshold()
        gst.debug_set_default_threshold(1)
        
        self._speed = 1.0
        self._time_format = gst.Format(gst.FORMAT_TIME)
        
        self._player = gst.element_factory_make("playbin", "player")
        self._xid = xid
        self._thread = GStreamerPlayer.SignalThread(window, self)
        self._thread.start()

        self._snapshot_conventer = GStreamerPlayer.SnapshotPipeline()
        
        self._was_eos = False
        
        # works
        #print gst.xml_write(self._player)

    def versions(self):
        return [
            ('GStreamer',   '.'.join(str(i) for i in gst.version()[:3])),
            ('PyGStreamer', pygst._pygst_version),
        ]

    def _cb_snapshot(self, element, buffer, pad):
        self._snapshot_buffer = buffer
        return True

    
    def _init_snapshot(self):
        
        if hasattr(self, '_snapshot_pipeline') and self._snapshot_pipeline is not None:
            return

        pipeline = ' ! '.join([
            'fakesrc name=src',
            'queue name=queue',
            'videoscale',
            'ffmpegcolorspace',
            'video/x-raw-rgb', # 'video/x-raw-rgb,width=160'
            'pngenc',
            'fakesink name=sink signal-handoffs=true'
        ])
        
        self._snapshot_pipeline = gst.parse_launch(pipeline)
        
        self._snapshot_queue = self._snapshot_pipeline.get_by_name('queue')
        self._snapshot_sink  = self._snapshot_pipeline.get_by_name('sink')

        self._snapshot_sink.connect('handoff', self._cb_snapshot)
        self._snapshot_pipeline.set_state(gst.STATE_PLAYING)
        
    def _do_snapshot(self):
        try:
            frame = self._player.props.frame.copy()
        except SystemError:
            return None

        data = self._snapshot_conventer.snapshot(frame)
        return ('png', data)
        

    def _cb_message(self, bus, message):
        t = message.type
        
        if t == gst.MESSAGE_ASYNC_DONE:
            pass
        elif t == gst.MESSAGE_EOS:
            self._was_eos = True
            self._player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self._was_eos = True
            self._player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_TAG:
            pass
            #print 'MESSAGE_TAG', '-' * 100
            #print message
            #print dir(message)
            #taglist = message.parse_tag()
            #print 'on_tag:'
            #for key in taglist.keys():
                #print '\t%s = %s' % (key, taglist[key])

    def _cb_sync_message(self, bus, message):
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == 'prepare-xwindow-id':
            imagesink = message.src
            imagesink.set_property('force-aspect-ratio', True)
            imagesink.set_xwindow_id(self._xid)

    def _seek(self, pos, wait=True):
        #self._player.seek(self._speed, gst.FORMAT_TIME,
            #gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            #gst.SEEK_TYPE_SET, pos,
            #gst.SEEK_TYPE_NONE, 0
        #)
            
        event = gst.event_new_seek(self._speed, gst.FORMAT_TIME,
            gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            gst.SEEK_TYPE_SET, pos,
            gst.SEEK_TYPE_NONE, 0
        )

        #event = gst.event_new_seek(self._speed, gst.FORMAT_TIME,
            #gst.SEEK_FLAG_FLUSH,
            #gst.SEEK_TYPE_SET, pos,
            #gst.SEEK_TYPE_NONE, 0
        #)

        res = self._player.send_event(event)
        if not res:
            raise InternalException
        
        if wait:
            msg = self._bus.poll(gst.MESSAGE_ASYNC_DONE, gst.SECOND * 3)

    def _pos(self):
        if self._time_format is None:
            return 0
        try:
            return self._player.query_position(self._time_format, None)[0]
        except gst.QueryError, e:
            return 0

    def _dur(self):
        if self._time_format is None:
            return 0
        try:
            return self._player.query_duration(self._time_format, None)[0]
        except gst.QueryError, e:
            return 0

    def _do_open(self, url, start=True):
        if url.startswith('/'):
            url = 'file://' + url
        self._player.set_property('uri', url)
        if start:
            self._player.set_state(gst.STATE_PLAYING)
        self._time_format = gst.Format(gst.FORMAT_TIME)
        
        #print 'audio', self._player.props.current_audio
        #print 'text ', self._player.props.current_text 
        #print 'video', self._player.props.current_video
        
        #for i in self._player.props.stream_info_value_array:
            #print 'nick   ', i.props.type.value_nick
            #print 'codec  ', i.props.codec
            #print 'decoder', i.props.language_code
            #print 'lang   ', i.props.language_code
            #print 'mute   ', i.props.mute
            #print 'caps   ', i.props.caps.to_string()
            
        #caps = self._player.props.frame.get_caps()[0]
        #for name in caps.keys():
            #print name, caps[name]
        
        
        #el = self._player.elements()
        #try:
            #while True:
                #next = el.next()
                #print 'str ', str(next)
                #print 'name', next.props.name
        #except StopIteration:
            #pass
        
    def _do_close(self):
        self._player.set_state(gst.STATE_NULL)
        
    def _do_get_state(self):
        cases = {
            gst.STATE_PLAYING: 'play',
            gst.STATE_PAUSED:  'pause',
            gst.STATE_READY:   'stop',
            gst.STATE_NULL:    'close',
        }
        if self._was_eos:
            return 'finish'
        else:
            return cases.get(self._player.get_state()[1], 'close')
    
    def _do_set_state(self, state):
        cases = {
            'play':   gst.STATE_PLAYING,
            'pause':  gst.STATE_PAUSED,
            'stop':   gst.STATE_READY,
            'close':  gst.STATE_NULL,
            'finish': gst.STATE_READY,
        }
        if state in cases:
            self._player.set_state(cases[state])
        
        self._was_eos = False

    def _do_get_speed(self):
        return self._speed

    def _do_set_speed(self, speed):
        if speed != self._speed:
            self._speed = speed
            self._seek(self._pos())

    def _do_get_volume(self):
        return self._player.get_property('volume') * 1.0

    def _do_set_volume(self, volume):
        volume = clamp(volume * 1.0, 0.0, 1.0)
        self._player.set_property('volume', volume)

