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


from lilyplayer.utils.play_time import Time
from lilyplayer.playlist.item import PlaylistItem

class PlaylistFormat(object):
	pass

class M3uPlaylist(PlaylistFormat):
    """ 
    """

    extension = 'm3u'

    @staticmethod
    def loads(data):
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

    @staticmethod
    def dumps(data):
        result = ['#EXTM3U']
        for i in data:
            if i.duration:
                result.append('#EXTINF:%d,%s' % (i.duration.total_seconds(), i.name))
            else:
                result.append('#EXTINF:%d,%s' % (0, i.name))
            result.append(i.filename)
        return '\n'.join(result)


class PlsPlaylist(PlaylistFormat):
    """ 
    """
    
    extension = 'pls'
    
    @staticmethod
    def loads(data):
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

    @staticmethod
    def dumps(data):
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



