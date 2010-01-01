#!/usr/bin/env python


import os
import os.path
import tempfile
import subprocess
import hashlib
import urllib
import logging

import struct
import xmlrpclib
import StringIO
import gzip
import base64
import pprint


import lilyplayer.utils.utils as utils
from lilyplayer.subtitles.subtitles import Subtitles


class SubtitleSource(object):
	def get_available(self, filename):
		"""
		Return list of typles in format:
		  (source, language, name, uid)
		"""
		pass
	
	def get_data(self, uid):
		pass
	
	def get_subtitles(self, item):
		data = self.get_data(item[3])
		#print data
		utils.File('~/sub.txt').write(data)
		subtitles = Subtitles()
		subtitles.load_string(data, encoding='cp1250')
		return subtitles
		
	
class LocalSource(SubtitleSource):
	def get_available(self, filename):
		"""
		Return list of typles in format:
		  (source, language, name, uid)
		"""
		filename = os.path.abspath(filename)
		basename = os.path.splitext(os.path.basename(filename))[0]
		directory = os.path.dirname(filename)
		
		result = []
		for fn in os.listdir(directory):
			if fn.endswith(('.txt', '.srt')):
				similar = utils.levenshtein_similarity(fn, basename)
				sub_file = os.path.join(directory, fn)
				result.append((similar, sub_file))
		
		result.sort()
		
		return [('lo', None, os.path.basename(f), f) for s, f in result]
		
	def get_data(self, uid):
		return utils.File(uid).read()


class NapiSource(SubtitleSource):
	def _mix(self, z):
		idx = [14,  3,  6,  8,  2] #[ 0xe, 0x3,  0x6, 0x8, 0x2 ]
		mul = [ 2,  2,  5,  4,  3]
		add = [ 0, 13, 16, 11,  5] #[   0, 0xd, 0x10, 0xb, 0x5 ]
		
		result = []
		
		for i, m, a in zip(idx, mul, add):
			t = a + int(z[i], 16)
			v = int(z[t:t + 2], 16)
			result.append(("%x" % (v*m))[-1])
		
		return ''.join(result)
	
	def get_available(self, filename):
		md5 = hashlib.md5()
		md5.update(open(filename).read(10485760))
		
		hexdigest = md5.hexdigest()
		mixdigest = self._mix(hexdigest)
	
		BASE_URL = "http://napiprojekt.pl/unit_napisy/dl.php"
		query = BASE_URL + "?" + urllib.urlencode([
			('l',       'PL'),
			('f',       hexdigest),
			('t',       mixdigest),
			('v',       'other'),
			('kolejka', 'false'),
			('nick',    ''),
			('pass',    ''),
			('napios',  os.name),
		])
		
		try:
			data = urllib.urlopen(query).read()
			return [('np', 'pl', os.path.basename(filename), data)]
		except IOError:
			return []
			
	def get_data(self, uid):
		handle, tmp7z = tempfile.mkstemp('.7z')
		os.close(handle)
		
		utils.File(tmp7z).write(uid)
		output = subprocess.Popen(['7z', 'x', '-y', '-so', '-piBlm8NTigvru0Jr0', tmp7z], stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
		os.remove(tmp7z)
		
		return output
	

# Code based on script 'subdl' by Karl Chen   http://www.cubewano.org/subdl/
class OpenSubtitlesSource(SubtitleSource):
	def __init__(self):
		super(OpenSubtitlesSource, self).__init__()
		SERVER_URL = "http://api.opensubtitles.org/xml-rpc"
		
		self.xmlrpc_server = xmlrpclib.Server(SERVER_URL)
		self.osdb_token = ""

	@staticmethod
	def movie_hash(name):
		longlongformat = '<Q'
		bytesize = struct.calcsize(longlongformat)
		assert bytesize == 8
		f = open(name, "rb")
		filesize = os.path.getsize(name)
		hash = filesize
		if filesize < 65536 * 2:
			raise Exception("Error hashing %s: file too small" %(name))
		for x in range(65536/bytesize):
			hash += struct.unpack(longlongformat, f.read(bytesize))[0]
			hash &= 0xFFFFFFFFFFFFFFFF
		f.seek(filesize-65536,0)
		for x in range(65536/bytesize):
			hash += struct.unpack(longlongformat, f.read(bytesize))[0]
			hash &= 0xFFFFFFFFFFFFFFFF
		f.close()
		return "%016x" % hash
	
	def get_available(self, filename):
		moviehash = OpenSubtitlesSource.movie_hash(filename)
		moviebytesize = os.path.getsize(filename)
		
		searchlist = [({
			#'sublanguageid': langs_search,
			'moviehash':     moviehash,
			'moviebytesize': str(moviebytesize)
		})]
		#print >>sys.stderr, "Searching for subtitles for moviehash=%s..." %(moviehash)
		try:
			results = self.xmlrpc_server.SearchSubtitles(self.osdb_token, searchlist)
		except Exception, e:
			#raise SystemExit("Error in XMLRPC SearchSubtitles call: %s"%e)
			print "Error in XMLRPC SearchSubtitles call: %s" % e
			return []
		data = results['data']
		#pprint.pprint(data)
		
		return [('os', i['ISO639'], i['SubFileName'], i) for i in data]
		#return data and [SubtitleSearchResult(d) for d in data]

	def get_data(self, uid):
		# TODO: test if use normal url download will be not better 
		#url = uid[]
		#data = urllib.urlopen(query).read()
		try:
			answer = self.xmlrpc_server.DownloadSubtitles(self.osdb_token,[uid['IDSubtitleFile']])
			data = answer['data']
			if not data:
				raise Exception("No data; status: %s"%answer['status'])
			subtitle_compressed = data[0]['data']
		except Exception, e:
			print e
			#raise SystemExit("Error in XMLRPC DownloadSubtitles call: %s"%e)
			
		gz = base64.decodestring(subtitle_compressed)
		return gzip.GzipFile(fileobj=StringIO.StringIO(gz)).read()


sources = {
	'lo': LocalSource(),
	'np': NapiSource(),
	'os': OpenSubtitlesSource()
}

def get_list(filename):
	result = []

	
	for src in sources:
		result.extend(sources[src].get_available(filename))
		
	return result


def get_subtitles(item):
	return sources[item[0]].get_subtitles(item)

if __name__ == '__main__':
	pass
"""
import subtitle_source as SS
napi = SS.NapiSource()
av = napi.get_available('/media/tv/dl/done/CSI.NY.S06E11.Second.Chances.HDTV.XviD-FQM.avi')
se = av[0]
su = napi.get_subtitles(se)
print su
"""