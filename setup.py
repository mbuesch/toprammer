#!/usr/bin/env python

from distutils.core import setup
import libtoprammer.main as toprammer_main

setup(	name		= "toprammer",
	version		= toprammer_main.VERSION,
	description	= "TOP2049 Open Source programming suite",
	author		= "Michael Buesch",
	author_email	= "m@bues.ch",
	url		= "http://bues.ch/h/toprammer",
	packages	= [ "libtoprammer", "libtoprammer/top2049", "libtoprammer/chips" ],
	package_data	= { "libtoprammer" : [ "fpga/bin/*.bit", "icons/*.png", ], },
	scripts		= [ "toprammer", "toprammer-gui", "toprammer-layout", ],
	keywords	= [ "universal programmer", "TOP", "TOP2049", ],
	classifiers	= [
		"Development Status :: 5 - Production/Stable",
		"Environment :: Console",
		"Environment :: X11 Applications",
		"Environment :: X11 Applications :: Qt",
		"Intended Audience :: Developers",
		"Intended Audience :: Education",
		"Intended Audience :: Information Technology",
		"Intended Audience :: Manufacturing",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
		"Operating System :: POSIX",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: Implementation :: CPython",
		"Topic :: Education",
		"Topic :: Scientific/Engineering",
		"Topic :: Software Development",
		"Topic :: Software Development :: Embedded Systems",
		"Topic :: Software Development :: Testing",
	],
)
