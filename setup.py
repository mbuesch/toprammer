#!/usr/bin/env python

from distutils.core import setup
import libtoprammer.toprammer_main as toprammer_main

setup(	name		= "toprammer",
	version		= toprammer_main.VERSION,
	description	= "TOP2049 Open Source programming suite",
	author		= "Michael Buesch",
	author_email	= "mb@bu3sch.de",
	url		= "http://bu3sch.de/joomla/index.php/toprammer-top2049",
	packages	= [ "libtoprammer", "libtoprammer/top2049", ],
	package_data	= { "libtoprammer" : [ "bit/*.bit" ], },
	scripts		= [ "toprammer", "toprammer-layout", "toprammer-unitest", ],
)
