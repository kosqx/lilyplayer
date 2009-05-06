#!/usr/bin/env python

import os
import glob
from distutils.core import setup


setup(
    name='Lily Player',
    version='0.4.1',
    license='GPL',
    description='Smart Media Player for Linux',
    long_description='Smart Media Player for Linux with powerfull support of playlists and subtitles', #ToDo: reStructuredText
    author='Krzysztof Kosyl',
    author_email='krzysztof.kosyl@gmail.com',
    #url='http://trac2.assembla.com/lilyplayer/',
    packages=[
        'lilyplayer',
        'lilyplayer.gui',
        'lilyplayer.player',
        'lilyplayer.subtitles',
        'lilyplayer.playlist',
        'lilyplayer.utils',
        'lilyplayer.info',
        
    ],
    data_files=[
        
        ('/usr/bin',                            ['lilyp']),
        ('/usr/share/lilyplayer/data',          ['data/mainicon.png']),
        ('/usr/share/lilyplayer/themes/black',  ['data/themes/black/controls.png',  'data/themes/black/controls.txt']),
        ('/usr/share/lilyplayer/themes/silver', ['data/themes/silver/controls.png', 'data/themes/silver/controls.txt']),
        #('/usr/share/lilyplayer/',              ['readme']),
        #('/usr/share/lilyplayer/',              ['license']),
        #('/usr/share/lilyplayer/',              ['data/icons/16x16/lilyplayer.png']),
        #('/usr/share/lilyplayer/gui',           ['data/gui/gtk_gui.glade']),
        #('/usr/share/lilyplayer/doc',           glob.glob("doc/*.html")),
        ('/usr/share/applications',             ['data/lilyplayer.desktop']),
        #('/usr/share/locale/pl/LC_MESSAGES',    po2mo(['po/pl/lilyplayer.po'])),
        ('/usr/share/icons/hicolor/16x16/apps', ['data/icons/16x16/lilyplayer.png']),
        ('/usr/share/icons/hicolor/22x22/apps', ['data/icons/22x22/lilyplayer.png']),
        ('/usr/share/icons/hicolor/32x32/apps', ['data/icons/32x32/lilyplayer.png']),
        ('/usr/share/icons/hicolor/48x48/apps', ['data/icons/48x48/lilyplayer.png']),
        ('/usr/share/icons/hicolor/64x64/apps', ['data/icons/64x64/lilyplayer.png']),
    ],
    classifiers = [
        'Topic :: Multimedia',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Environment :: Console',
        'Environment :: X11 Applications'

        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: GNU General Public License (GPL)',

        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ],
)
 
