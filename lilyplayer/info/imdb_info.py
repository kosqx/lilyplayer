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

import os.path
import re
import urllib
import md5
import logging


import imdb
from mako.template import Template


import lilyplayer.settings as settings
import lilyplayer.utils.utils as utils

'''
Todo
import lilyplayer.info as info

self.movie_info = info.MediaInfo(country=['usa', 'pl'])

return 

'''


class MediaInfoException(Exception):
    pass


def make_file_hash(filename):
    # Deprecated since version 2.5: Use the hashlib module instead.
    try:
        data = utils.File(filename).read(size=1024*1024)
        hash = md5.new()
        hash.update(data)
        return hash.hexdigest()
    except:
        return None
        

class MovieCache():
    def __init__(self, filename):
        self._filename = filename
        
        try:
            data = utils.File(filename).read(size=1024*1024)
            hash = md5.new()
            hash.update(data)
            self._hash = hash.hexdigest()
        except:
            raise Exception()
        
        self._keys = {
            'cover': 'cover.img'
        }
        self._data = {}
        
    def get_filename(self):
        return self._filename
    
    def get_hash(self):
        return self._hash
    
    def __getitem__(self, key):
        if key not in self._data:
            if key in self._keys:
                filename = self._keys[key]
            else:
                filename = 'cache.db'
            
            path = settings.get_path('~', 'cache', self._hash, 'cover.jpg')
            result = None
            
            if utils.File(info_path_img).exists():
                data = utils.File(path).read()
                
            else:
                if key in self._keys:
                    result = ''
                else:
                    result = {}
            self._data[key] = result
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
        if key in self._keys:
            pass


class MediaInfo:
    CAST_LIMIT = 50
    
    def filename2title(self, filename):
        series = [
            r's(?P<season>[0-9]+)(?P<episodes>(e[0-9]+)+)',
            r'(?P<season>[0-9]+)x(?P<episodes>([0-9]+)([-,][0-9]+)*)',
            r'(?P<episodes>(e[0-9]+)+)',
        ]

        formats = '(' + '|'.join([
            'brrip', 'dvdrip', 'dvdscr', 'scr', 'svcd', 'vcd', 'tc', 'ts', 'cam', 'r5', 'hdtv', 'tvrip',
            'xvid', 'divx', 'x264',
            'ac3', 'aac', 'mp3',
        ]) + ')'

        remove = [
            r'\.|\[|\]|\(|\)',
            r' %s-[a-z0-1]+ ' % formats,
            formats,
            r' part ',
            r' (19|20)[0-9][0-9] ',
            r' eng ', r' en ', r' pl ',
            r'-', r'  +'
        ]
        
        season = None
        episodes = None

        
        name = ' ' + os.path.splitext(os.path.split(filename)[-1])[0] + ' '
        name = name.lower()
        
        for s in series:
            m = re.search(s, name)
            if m:
                name = re.split(s, name)[0]
                d = m.groupdict()
                season = int(d.get('season', '1'))
                episodes = re.split('([0-9]+)', d['episodes'])
                episodes = [int(i) for i in episodes[1::2]]
        
        for r in remove:
            # change to split
            name = re.sub(r, ' ', name)
        
        name = name.strip()
        
        logging.debug('filename2title name=%r, season=%r, episodes=%r' % (name, season, episodes))
        
        return name, season, episodes
    
    def _read_url(self, url):
        f = urllib.urlopen(url)
        data = f.read()
        f.close()
        return data
    
    def get_info(self, filename):
        # TODO: keyword arguments
        # filename  - guest title from filename and search
        # title     - search from title
        # imdb_id   - internal IMDb id - instant movie info load - without search
        
        info = {}
        
        logging.debug('get_info start')
        
        file_hash = make_file_hash(filename)
        logging.debug('File hash: %r' % file_hash)
        
        name, season, episodes =  self.filename2title(filename)
        
        db = imdb.IMDb()
        imdb_results = db.search_movie(name)
        imdb_movie = imdb_results[0]
        
        info['kind'] = 'movie'
        info['list'] = ['%s (%d)' % (i['title'], i['year']) for i in imdb_results]
        logging.debug('imdb searched')
        
        db.update(imdb_movie)
        
        logging.debug('imdb updated')
        
        info['title'] = imdb_movie['title']
        info['cover_url'] = imdb_movie['cover url']
        info['year'] = imdb_movie['year']
        try:
            info['time'] = imdb_movie['runtime'][0]
        except KeyError:
            pass
        #info['time'] = imdb_movie['runtime'][0]
        info['rating'] = imdb_movie['rating']
        info['votes'] = imdb_movie['votes']
        info['languages'] = imdb_movie['languages']
        info['genres'] = imdb_movie['genres']
        info['countries'] = imdb_movie['countries']
        try:
            info['plot'] = imdb_movie['plot'][0].rsplit('::', 1)[0]
        except KeyError:
            pass
        

        def character_to_dict(character):
            try:
                role = character.currentRole['long imdb name']
            except:
                role = ''
            
            return dict(
                imdb_id=character.getID(),
                name=character['long imdb name'],
                role=role
            )
        
        cast = []
        for character in imdb_movie['cast'][:MediaInfo.CAST_LIMIT]:
            cast.append(character_to_dict(character))

            
        
        info['cast'] = cast
        
        
        if imdb_movie['kind'] == 'tv series' and season is not None:
            info['kind'] = 'series'
            db.update(imdb_movie, 'episodes')
            #db.update(imdb_movie, 'guests')
            logging.debug('imdb episodes')
            imdb_episode = imdb_movie['episodes'][season][episodes[0]]
            db.update(imdb_episode, 'full credits')
            info['season']        = imdb_episode['season']
            info['episode']       = imdb_episode['episode']
            info['episode_title'] = imdb_episode['title']
            try:
                info['episode_plot'] = imdb_episode['plot']
            except KeyError:
                pass
            info['episode_air_date'] = imdb_episode['original air date']
            #print imdb_episode['cast']
            
            
            general_cast_ids = [i['imdb_id'] for i in info['cast']]
            episode_cast = []
            for character in imdb_episode['cast']:
                if character.getID not in general_cast_ids:
                    cast.append(character_to_dict(character))
            
            info['episode_cast'] = episode_cast
            
            #ia.update(ep)
            #self.add('<h2>%s</h2>' % ep['title'])
            #self.add('<b>Season %s Episode %s</b>', (ep['season'], ep['episode']))
        
        
        logging.debug('imdb end')
        return info
    
    def get_html(self, info):
        #img = None
        #info_path_img = settings.get_path('~', 'cache', file_hash, 'cover.jpg')
        #if utils.File(info_path_img).exists():
        #    img = utils.File(info_path_img).read()
        #
        #info_path_data = settings.get_path('~', 'cache', file_hash, 'info.db')
        #if utils.File(info_path_data).exists():
        #    return utils.File(info_path_data).read(), img
        
        mytemplate = Template(u'''
<h1>${info['title']}</h1>

% if info['kind'] == 'series':
    <h2>${info['episode_title']}</h2><br />
    <b>Season ${info['season']} Episode ${info['episode']}</b>
% endif

<br/><img src="mem://cover" />

<table>
    <tr>
        <td>Year</td>
        <td>${info['year']}</td>
    </tr>
    
    % if 'time' in info:
    <tr>
        <td>Year</td>
        <td>${info['time']} min.</td>
    </tr>
    % endif
    
    % if 'episode_air_date' in info:
        <tr>
            <td>Air date</td>
            <td>${info['episode_air_date']}</td>
        </tr>
    % endif
    
    <tr>
        <td>Rating</td>
        <td>${info['rating']}</td>
    </tr>
    <tr>
        <td>Votes</td>
        <td>${info['votes']}</td>
    </tr>
    <tr>
        <td>Languages</td>
        <td>${', '.join(info['languages'])}</td>
    </tr>
    <tr>
        <td>Genres</td>
        <td>${', '.join(info['genres'])}</td>
    </tr>
    <tr>
        <td>Countries</td>
        <td>${', '.join(info['countries'])}</td>
    </tr>
</table>

% if 'plot' in info:
    <h2>Plot</h2>
    <p>
        ${info['plot']}
    </p>
% endif

% if 'episode_plot' in info:
    <h2>Episode plot</h2>
    <p>
        ${info['episode_plot'].encode('ascii', 'xmlcharrefreplace')}
    </p>
% endif

<h2>Cast</h2>

<table>
    % for actor in info['cast']:
        <tr>
            <td><b>${actor['name']}</b></td>
            <td>${actor['role']}</td>
        </tr>
    % endfor
</table>
<hr />
% if 'episode_cast' in info and info['episode_cast']:
    <table>
        % for actor in info['episode_cast']:
            <tr>
                <td><b>${actor['name']}</b></td>
                <td>${actor['role']}</td>
            </tr>
        % endfor
    </table>
% endif
        ''')
        
        html = mytemplate.render(info=info)
        data = {'cover': self._read_url(info['cover_url'])}
        
        #utils.File(info_path_data).write(html)
        #if img:
        #    utils.File(info_path_img).write(img)
        
        return html, data

