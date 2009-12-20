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


audio = {
	'mka':   ('Matroska audio',    ['mka'], ['audio/x-matroska']),
	'oga':   ('Ogg Audio',    ['oga'], ['audio/ogg']),
	'ogg':   ('Ogg Vorbis audio',    ['ogg'], ['audio/x-vorbis+ogg']),
	'ogg':   ('Ogg FLAC audio',    ['ogg'], ['audio/x-flac+ogg']),
	'ogg':   ('Ogg Speex audio',    ['ogg'], ['audio/x-speex+ogg']),
	'spx':   ('Speex audio',    ['spx'], ['audio/x-speex']),
	'shn':   ('Shorten audio',    ['shn'], ['application/x-shorten']),
	'ac3':   ('Dolby Digital audio',    ['ac3'], ['audio/ac3']),
	'amr':   ('Adaptive Multi-Rate',    ['amr'], ['audio/amr']), # TODO: wiki
	'awb':   ('Adaptive Multi-Rate Wideband',    ['awb'], ['audio/amr-wb']),
	'snd':   ('ULAW (Sun) audio',    ['snd', 'au'], ['audio/basic']),
	'sid':   ('Commodore 64 audio',    ['sid', 'psid'], ['audio/prs.sid']),
	'pcm':   ('PCM audio',    [], ['audio/x-adpcm']),
	'aifc':  ('AIFC audio',    [], ['audio/x-aifc']),
	'aiff':  ('AIFF/Amiga/Mac audio',    ['aiff', 'aif', 'aifc'], ['audio/x-aiff']),
	'ape':   ('Monkey\'s audio',    ['ape'], ['audio/x-ape']),
	'it':    ('Impulse Tracker audio',    ['it'], ['audio/x-it']),
	'flac':  ('FLAC audio',    ['flac'], ['audio/x-flac']),
	'wvp':   ('WavPack audio',    ['wv', 'wvp'], ['audio/x-wavpack']),
	'wvc':   ('WavPack audio correction file',    ['wvc'], ['audio/x-wavpack-correction']),
	'midi':  ('MIDI audio',    ['midi', 'mid', 'kar'], ['audio/midi']),
	'm4a':   ('MPEG-4 audio',    ['m4a', 'aac'], ['audio/mp4']),
	'm4b':   ('MPEG-4 audio book',    ['m4b'], ['audio/x-m4b']),
	'mod':   ('Amiga SoundTracker audio',    ['mod', 'ult', 'uni', 'm15', 'mtm', '669'], ['audio/x-mod']),
	'mp2':   ('MP2 audio',    ['mp2'], ['audio/mp2']),
	'mp3':   ('MP3 audio',    ['mp3', 'mpga'], ['audio/mpeg']),
	'psf':   ('PSF audio',    ['psf'], ['audio/x-psf']),
	'mpsf':  ('Miniature Portable Sound Format',    ['minipsf'], ['audio/x-minipsf']),
	'psfl':  ('Portable Sound Format Library',    ['psflib'], ['audio/x-psflib']),
	'wma':   ('Windows Media audio',    ['wma'], ['audio/x-ms-wma']),
	'mpc':   ('Musepack audio',    ['mpc', 'mpp', 'mp'], ['audio/x-musepack']),
	'ra':    ('RealAudio document',    ['ra', 'rax'], ['audio/vnd.rn-realaudio']),
	'riff':  ('RIFF audio',    [], ['audio/x-riff']),
	'voc':   ('VOC audio',    ['voc'], ['audio/x-voc']),
	'wav':   ('WAV audio',    ['wav'], ['audio/x-wav']),
	'xi':    ('Scream Tracker instrument',    ['xi'], ['audio/x-xi']),
	'xm':    ('FastTracker II audio',    ['xm'], ['audio/x-xm']),
	'tta':   ('TrueAudio audio',    ['tta'], ['audio/x-tta']),
}


video = {
	'flv':   ('Flash video',                     ['flv'], ['application/x-flash-video']),
	'mkv':   ('Matroska video',                  ['mkv'], ['video/x-matroska']),
	'ogv':   ('Ogg Video',                       ['ogv'], ['video/ogg']),
	'ogg':   ('Ogg Theora video',                ['ogg'], ['video/x-theora+ogg']),
	'ogm':   ('OGM video',                       ['ogm'], ['video/x-ogm+ogg']),
	'mp4':   ('MPEG-4 video',                    ['mp4', 'm4v'], ['video/mp4']),
	'3gp':   ('3GPP multimedia',                 ['3gp', '3gpp', 'amr'], ['video/3gpp']),
	'rv':    ('RealVideo document',              ['rv', 'rvx'], ['video/vnd.rn-realvideo']),
	'dv':    ('Digital Video',                   ['dv'], ['video/dv']),
	'mpeg':  ('Moving Picture Experts Group',    ['mpeg', 'mpg', 'mp2', 'mpe', 'vob', 'm2t'], ['video/mpeg']),
	'mov':   ('QuickTime video',                 ['mov', 'qt', 'moov', 'qtvr'], ['video/quicktime']),
	'vivo':  ('Vivo video',                      ['vivo', 'viv'], ['video/vivo']),
	'flic':  ('FLIC animation',                  ['fli', 'flc'], ['video/x-flic']),
	'mng':   ('Multiple-Image Network Graphics', ['mng'], ['video/x-mng']),
	'asf':   ('Advanced Streaming Format',       ['asf'], ['video/x-ms-asf']),
	'wmv':   ('Windows Media video',             ['wmv'], ['video/x-ms-wmv']),
	'avi':   ('Audio Video Interleave',          ['avi', 'divx'], ['video/x-msvideo']),
	'nsv':   ('NullSoft video',                  ['nsv'], ['video/x-nsv']),
	'movie': ('SGI video',                       ['movie'], ['video/x-sgi-movie']),
	
	#'anim': ('ANIM animation',                  [''], ['video/x-anim']),
	#dict(type="video/x-anim", description="ANIM animation", priority="100", pattern="*.anim[1-9j]")
}

