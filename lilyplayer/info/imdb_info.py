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


import imdb

import lilyplayer.settings as settings
import lilyplayer.utils.utils as utils

'''
Todo
import lilyplayer.info as info

self.movie_info = info.MovieInfo(country=['usa', 'pl'])

return 

'''


class MovieInfoException(Exception):
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
            
            
    
        

class MovieInfo():
    def get_info(self):
        file_hash = make_file_hash(filename)
        
        img = None
        info_path_img = settings.get_path('~', 'cache', file_hash, 'cover.jpg')
        if utils.File(info_path_img).exists():
            img = utils.File(info_path_img).read()
            
        info_path_data = settings.get_path('~', 'cache', file_hash, 'info.db')
        if utils.File(info_path_data).exists():
            return utils.File(info_path_data).read(), img
        
       
        try:
        
            print 'imdb start ' * 100
            
            name, season, episodes =  self._filename2title(filename)
            ia = imdb.IMDb()
            ir = ia.search_movie(name)
            if not ir:
                return ''
            
            
            # select item using rating 
            
            if season is None:
                rate_kind = 'movie'
            else:
                rate_kind = 'tv series'

            rate_list = []
            
            for item in ir:
                print item['kind']
                rate_val = (item['kind'] != rate_kind) * 10
                rate_val += utils.levenshtein_distance(name, item['title'].lower()) * 2
                try:
                    rate_val += abs(item['year'] - 2005)
                except KeyError:
                    pass
                rate_list.append((rate_val, item))
                #print item.items()
            rate_list.sort()
            
            print rate_list
            
            self.movie = rate_list[0][1]
            
            
            
            
            #self.movie = ir[0]
            
            ia.update(self.movie)
            
            # ia.update(im, 'release_dates')
            # im['release dates']
            # [u'USA::11 December 2005 (Austin Butt-Numb-A-Thon)', u'Poland::7 April 2006']

            self.result = []
            
    
            #self.add('<h1>%(canonical title)s</h1>')
            self.add('<h1>%(title)s</h1>')
            
            if self.movie['kind'] == 'tv series' and season is not None:
                ia.update(self.movie, 'episodes')
                ep = self.movie['episodes'][season][episodes[0]]
                #ia.update(ep)
                self.add('<h2>%s</h2>' % ep['title'])
                self.add('<b>Season %s Episode %s</b>', (ep['season'], ep['episode']))
            
            self.add('<a href="http://www.google.com">Google</a>')
            
            #self.add('<img src="%(cover url)s">')
            self.add('<br/><img src="mem://image"/>')
            self.add('<table>')
            self.add('<tr><td>Year</td><td>%(year)s</td></tr>')
            try:
                self.add('<tr><td>Runtime</td><td>%s min.</td></tr>', self.movie['runtime'][0])
            except KeyError:
                pass
            self.add('<tr><td>Rating</td><td>%(rating)s</td></tr>')
            self.add('<tr><td>Votes</td><td>%(votes)s</td></tr>')
            try:
                self.add('<tr><td>Languages</td><td>%s</td></tr>', ', '.join(self.movie['languages']))
            except KeyError:
                pass
            self.add('<tr><td>Genres</td><td>%s</td></tr>', ', '.join(self.movie['genres']))
            self.add('<tr><td>Countries</td><td>%s</td></tr>', ', '.join(self.movie['countries']))
            
            self.add('</table>')
            self.add('<h2>Cast</h2>')
            
            self.add('<table>')
            for actor in self.movie['cast'][:IMDbInfo.CAST_LIMIT]:
                try:
                    role = actor.currentRole['long imdb name']
                except:
                    role = ''
                    print actor.items()
                    
                self.add('<tr><td><b>%(name)s</b></td><td>%(role)s</td></tr>' % dict(
                    name=actor['long imdb name'],
                    role=role
                ))
            self.add('</table>')
            
            print 'imdb end ' * 100
            
            try:
                img = self._read_url(self.movie['cover url'])
            except:
                img = None
            
            
            html = '\n'.join(self.result)
            utils.File(info_path_data).write(html)
            
            if img:
                utils.File(info_path_img).write(img)
            
            return html, img
        
        except Exception, e:
            print type(e), e
            return '', None
    

    

class IMDbInfo:
    
    CAST_LIMIT = 50
    
    def _filename2title(self, filename):
        
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
            print s
            m = re.search(s, name)
            if m:
                name = re.split(s, name)[0]
                d = m.groupdict()
                season = int(d.get('season', '1'))
                episodes = re.split('([0-9]+)', d['episodes'])
                episodes = [int(i) for i in episodes[1::2]]
        
        print name
        for r in remove:
            # change to split
            name = re.sub(r, ' ', name)
            print name
        
        name = name.strip()
        
        print 'name, season, episodes', name, season, episodes
        
        return name, season, episodes
    
    
    
    def add(self, format, data=None):
        if data is None:
            data = self.movie
        try:
            self.result.append(format % data)
        except KeyError:
            pass
        
        
    def _read_url(self, url):
        f = urllib.urlopen(url)
        data = f.read()
        f.close()
        return data
    
    def download_info(self, name, year, season, episodes):
        d = {}
        
        ia = imdb.IMDb()
        ir = ia.search_movie(name)
        
        if season is None:
            rate_kind = 'movie'
        else:
            rate_kind = 'tv series'

        rate_list = []
        
        for item in ir:
            rate_val = (item['kind'] != rate_kind) * 10
            rate_val += utils.levenshtein_distance(name, item['title'].lower()) * 2
            try:
                rate_val += abs(item['year'] - 2005)
            except KeyError:
                pass
            rate_list.append((rate_val, item))
        
        rate_list.sort()
        movie = rate_list[0][1]
        
        d['title'] = movie['title']
        d['kind'] = movie['title']
        d['year']  = movie['year']
        
        
        d['title'] = movie['title']
        d['title'] = movie['title']
            


    def get_info(self, filename):
        print 'get_info ' * 10
        
        file_hash = make_file_hash(filename)
        
        img = None
        info_path_img = settings.get_path('~', 'cache', file_hash, 'cover.jpg')
        if utils.File(info_path_img).exists():
            img = utils.File(info_path_img).read()
            
        info_path_data = settings.get_path('~', 'cache', file_hash, 'info.db')
        if utils.File(info_path_data).exists():
            return utils.File(info_path_data).read(), img
        
       
        try:
        
            print 'imdb start ' * 100
            
            name, season, episodes =  self._filename2title(filename)
            ia = imdb.IMDb()
            ir = ia.search_movie(name)
            if not ir:
                return ''
            
            
            # select item using rating 
            
            if season is None:
                rate_kind = 'movie'
            else:
                rate_kind = 'tv series'

            rate_list = []
            
            for item in ir:
                print item['kind']
                rate_val = (item['kind'] != rate_kind) * 10
                rate_val += utils.levenshtein_distance(name, item['title'].lower()) * 2
                try:
                    rate_val += abs(item['year'] - 2005)
                except KeyError:
                    pass
                rate_list.append((rate_val, item))
                #print item.items()
            rate_list.sort()
            
            print rate_list
            
            self.movie = rate_list[0][1]
            
            
            
            
            #self.movie = ir[0]
            
            ia.update(self.movie)
            
            # ia.update(im, 'release_dates')
            # im['release dates']
            # [u'USA::11 December 2005 (Austin Butt-Numb-A-Thon)', u'Poland::7 April 2006']

            self.result = []
            
    
            #self.add('<h1>%(canonical title)s</h1>')
            self.add('<h1>%(title)s</h1>')
            
            if self.movie['kind'] == 'tv series' and season is not None:
                ia.update(self.movie, 'episodes')
                ep = self.movie['episodes'][season][episodes[0]]
                #ia.update(ep)
                self.add('<h2>%s</h2>' % ep['title'])
                self.add('<b>Season %s Episode %s</b>', (ep['season'], ep['episode']))
            
            self.add('<a href="http://www.google.com">Google</a>')
            
            #self.add('<img src="%(cover url)s">')
            self.add('<br/><img src="mem://image"/>')
            self.add('<table>')
            self.add('<tr><td>Year</td><td>%(year)s</td></tr>')
            try:
                self.add('<tr><td>Runtime</td><td>%s min.</td></tr>', self.movie['runtime'][0])
            except KeyError:
                pass
            self.add('<tr><td>Rating</td><td>%(rating)s</td></tr>')
            self.add('<tr><td>Votes</td><td>%(votes)s</td></tr>')
            try:
                self.add('<tr><td>Languages</td><td>%s</td></tr>', ', '.join(self.movie['languages']))
            except KeyError:
                pass
            self.add('<tr><td>Genres</td><td>%s</td></tr>', ', '.join(self.movie['genres']))
            self.add('<tr><td>Countries</td><td>%s</td></tr>', ', '.join(self.movie['countries']))
            
            self.add('</table>')
            self.add('<h2>Cast</h2>')
            
            self.add('<table>')
            for actor in self.movie['cast'][:IMDbInfo.CAST_LIMIT]:
                try:
                    role = actor.currentRole['long imdb name']
                except:
                    role = ''
                    print actor.items()
                    
                self.add('<tr><td><b>%(name)s</b></td><td>%(role)s</td></tr>' % dict(
                    name=actor['long imdb name'],
                    role=role
                ))
            self.add('</table>')
            
            print 'imdb end ' * 100
            
            try:
                img = self._read_url(self.movie['cover url'])
            except:
                img = None
            
            
            html = '\n'.join(self.result)
            utils.File(info_path_data).write(html)
            
            if img:
                utils.File(info_path_img).write(img)
            
            return html, img
        
        except Exception, e:
            print type(e), e
            return '', None
        
        
        
        
    
    
    
    