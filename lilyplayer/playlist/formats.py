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


import lilyplayer.utils.utils as utils
from lilyplayer.utils.play_time import Time
from lilyplayer.playlist.item import PlaylistItem, PlaylistError


class PlaylistFormat(object):
    def __init__(self):
        super(PlaylistFormat, self).__init__()
        
        if not hasattr(self, 'name'):
            glob = globals()
            self._formats = {}
            self._extensions = {}
            self._mimes = {}
            for i in glob:
                obj = glob[i]
                if obj.__class__.__name__ == 'type' and PlaylistFormat in obj.mro()[1:]:
                    self._formats[obj.name] = obj()
                    for e in obj.extensions:
                        self._extensions[e] = obj.name
                    for m in obj.mimes:
                        self._mimes[m] = obj.name
                        
            print self._formats, self._extensions, self._mimes

    def __getitem__(self, key):
        if key in self._formats:
            return self._formats[key]
        if key in self._extensions:
            return self._formats[self._extensions[key]]
        if key in self._mimes:
            return self._formats[self._mimes[key]]
        raise PlaylistError, 'Playlist format %r unknown' % key
    
    def __iter__(self):
        return iter(self._formats)
        
        
    def load(self, path):
        data = utils.File(path).read()
        return self.loads(data)
        
    def dump(self, data, path):
        data = self.dumps(data)
        utils.File(path).write(data)


class M3uPlaylist(PlaylistFormat):
    name       = 'm3u'
    label      = 'MP3 audio (streamed)'
    extensions = ['m3u', 'vlc']
    mimes      = ['audio/x-mpegurl']

    def loads(self, data):
        lines = [l.strip() for l in data.splitlines()]
        lines = [l for l in lines if len(l) > 0]
        extended = False
        if lines[0] == '#EXTM3U':
            extended = True
            lines = lines[1:]

        result = []
        lasttime, lastname = None, None

        for line in lines:
            if line.startswith('#'):
                if line.startswith('#EXTINF:'):
                    try:
                        a = line.split(':', 1)[1].split(',', 1)
                        lasttime = int(a[0])
                        lastname = a[1]
                        if lasttime < 0:
                            lasttime = None
                        else:
                            lasttime = Time(s=lasttime)
                    except:
                        lasttime, lastname = None, None
            else:
                result.append(PlaylistItem(
                        filename=line, name=lastname, duration=lasttime))
                lasttime, lastname = None, None

        return result

    def dumps(self, data):
        result = ['#EXTM3U']
        for i in data:
            if i.duration:
                result.append('#EXTINF:%d,%s' % (i.duration.total_seconds(), i.name))
            else:
                result.append('#EXTINF:%d,%s' % (-1, i.name))
            result.append(i.filename)
        return '\n'.join(result)


class PlsPlaylist(PlaylistFormat):
    name       = 'pls'
    label      = 'MP3 ShoutCast playlist'
    extensions = ['pls']
    mimes      = ['audio/x-scpls']
    
    def loads(self, data):
        def add(d, key):
            if not d.has_key(key):
                d[key] = ['', '', Time()]
            return d[key]

        lines = [l.strip() for l in data.splitlines()]
        lines = [l for l in lines if len(l) > 0]
        result = []
        tmp = {}

        if lines[0].lower() == '[playlist]':
            lines = lines[1:]

        for line in lines:
            try:
                a = line.split('=', 1)
                cmd = a[0].strip().lower()
                arg = a[1].strip()
                if cmd.startswith('file'):
                    i = int(cmd[4:])
                    add(tmp, i)[0] = arg
                elif cmd.startswith('title'):
                    i = int(cmd[5:])
                    add(tmp, i)[1] = arg
                elif cmd.startswith('length'):
                    i = int(cmd[6:])
                    time = int(arg)
                    if time > 0:
                        add(tmp, i)[2] = Time(s = int(arg))
            except:
                pass
        keys = tmp.keys()
        keys.sort()
        for k in keys:
            a = tmp[k]
            result.append(PlaylistItem(
                filename=a[0], name=a[1], duration=a[2]))
        return result

    def dumps(self, data):
        result = ['[playlist]', 'NumberOfEntries=%d' % len(data), '']

        for i, d in enumerate(data):
            result.append('File%d=%s' % (i + 1, d.filename))
            if d.name:
                result.append('Title%d=%s' % (i + 1, d.name))
            if d.duration:
                result.append('Length%d=%s' % (i + 1, d.duration.totalSeconds()))
            result.append('')
        result.append('Version=2')
        return '\n'.join(result)


## Currently only format spec
#
#class XspfPlaylist(PlaylistFormat):
#    name =       'xspf'
#    label =      'XML Shareable Playlist Format'
#    extensions = ['xspf']
#    mimes =      ['application/xspf+xml']
#    
#class PlaPlaylist(PlaylistFormat):
#    name =       'pla'
#    label =      'iRiver Playlist'
#    extensions = ['pla']
#    mimes =      ['audio/x-iriver-pla']
#    
#class QtlPlaylist(PlaylistFormat):
#    name       = 'qtl'
#    label      = 'QuickTime metalink playlist'
#    extensions = ['qtl']
#    mimes      = ['application/x-quicktime-media-link']
#    
#class AsxPlaylist(PlaylistFormat):
#    name       = 'asx'
#    label      = 'Microsoft ASX playlist'
#    extensions = ['asx', 'wax', 'wvx', 'wmx']
#    mimes      = ['audio/x-ms-asx']

