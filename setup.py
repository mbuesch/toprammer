#!/usr/bin/env python

from distutils.core import setup
import libtoprammer.toprammer_main as toprammer_main

setup(	name		= "toprammer",
	version		= toprammer_main.VERSION,
	description	= "TOP2049 Open Source programming suite",
	author		= "Michael Buesch",
	author_email	= "m@bues.ch",
	url		= "http://bues.ch/cms/hacking/toprammer.html",
	packages	= [ "libtoprammer", "libtoprammer/top2049", ],
	package_data	= { "libtoprammer" : [ "bit/*.bit", "icons/*.png", ], },
	scripts		= [ "toprammer", "toprammer-gui", "toprammer-layout", ],
)
