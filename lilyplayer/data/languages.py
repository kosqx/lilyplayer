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


## Format:
# (ISO 639-1, ISO 639-2, Name in English, Name in language itself (Native))

languages_data = [
    ('ar', 'ara', 'Arabic',        u'العربية'),
    ('bg', 'bul', 'Bulgarian',     u'български език'),
    ('bs', 'bos', 'Bosnian',       u'bosanski jezik'),
    ('ca', 'cat', 'Catalan',       u'Català'),
    ('cs', 'cze', 'Czech',         u'Čeština'),
    ('da', 'dan', 'Danish',        u'Dansk'),
    ('de', 'ger', 'German',        u'Deutsch'),
    ('el', 'ell', 'Greek',         u'Ελληνικά'),
    ('en', 'eng', 'English',       u'English'),
    ('eo', 'epo', 'Esperanto',     u'Esperanto'),
    ('es', 'spa', 'Spanish',       u'Español'),
    ('et', 'est', 'Estonian',      u'Eesti keel'),
    ('fa', 'per', 'Farsi',         u'فارسی'),
    ('fi', 'fin', 'Finnish',       u'Suomi'),
    ('fr', 'fre', 'French',        u'Français'),
    ('gl', 'glg', 'Galician',      u'Galego'),
    ('he', 'heb', 'Hebrew',        u'עִבְרִית'),
    ('hi', 'hin', 'Hindi',         u'हिन्दी'), #TODO:flag
    ('hr', 'hrv', 'Croatian',      u'Hrvatski jezik'),
    ('hu', 'hun', 'Hungarian',     u'Magyar'),
    ('hy', 'arm', 'Armenian',      u'Հայերեն'),
    ('id', 'ind', 'Indonesian',    u'Bahasa Indonesia'),
    ('is', 'ice', 'Icelandic',     u'Íslenska'),
    ('it', 'ita', 'Italian',       u'Italiano'),
    ('ja', 'jpn', 'Japanese',      u'日本語'),
    ('ka', 'geo', 'Georgian',      u'Georgian'),
    ('kk', 'kaz', 'Kazakh',        u'Қазақ тілі'),
    ('ko', 'kor', 'Korean',        u'한국어'),
    ('lb', 'ltz', 'Luxembourgish', u'Lëtzebuergesch'),
    ('lt', 'lit', 'Lithuanian',    u'lietuvių kalba'),
    ('lv', 'lav', 'Latvian',       u'latviešu valoda'),
    ('mk', 'mac', 'Macedonian',    u'македонски јазик'),
    ('ms', 'may', 'Malay',         u'Malay'),
    ('nl', 'dut', 'Dutch',         u'Nederlands'),
    ('no', 'nor', 'Norwegian',     u'Norsk'),
    ('oc', 'oci', 'Occitan',       u'Occitan'),
    ('pb', 'pob', 'Portuguese-BR', u'Portuguęs (BR)'),
    ('pl', 'pol', 'Polish',        u'Polski'),
    ('pt', 'por', 'Portuguese',    u'Português'),
    ('ro', 'rum', 'Romanian',      u'Română'),
    ('ru', 'rus', 'Russian',       u'русский язык'),
    ('si', 'sin', 'Sinhalese',     u'සිංහල'),
    ('sk', 'slo', 'Slovak',        u'Slovenčina'),
    ('sl', 'slv', 'Slovenian',     u'Slovenščina'),
    ('sq', 'alb', 'Albanian',      u'Shqip'),
    ('sr', 'scc', 'Serbian',       u'Cрпски'),
    ('sv', 'swe', 'Swedish',       u'Svenska'),
    ('th', 'tha', 'Thai',          u'ภาษาไทย'),
    ('tl', 'tgl', 'Tagalog',       u'Tagalog'),
    ('tr', 'tur', 'Turkish',       u'Türkçe'),
    ('uk', 'ukr', 'Ukrainian',     u'Українська'),
    ('ur', 'urd', 'Urdu',          u'اردو'), #TODO: flag
    ('vi', 'vie', 'Vietnamese',    u'Tiếng Việt'),
    ('zh', 'chi', 'Chinese',       u'中文'),
]


class Language(object):
    def __init__(self, iso1, iso2, name, native):
        super(Language, self).__init__()
        
        self.iso1   = iso1
        self.iso2   = iso2
        self.name   = name
        self.native = native


languages = {}
for l in languages_data:
    lang = Language(*l)
    for i in l:
        languages[i] = lang

