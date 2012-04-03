"""
#    TOP2049 Open Source programming suite
#
#    TOP2049 GND layout definitions
#
#    Copyright (c) 2010 Michael Buesch <m@bues.ch>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import sys
if __name__ == "__main__":
	sys.path.insert(0, sys.path[0] + "/../..")
from libtoprammer.generic_layout import *


class GNDLayout(GenericLayout):
	# A list of valid ZIF GND pins (0=none)
	validPins = (0, 5, 14, 15, 16, 17, 18, 19, 20, 24, 26, 27,
		28, 29, 33, 34, 35)

	def __init__(self, top=None):
		GenericLayout.__init__(self, nrZifPins=48)
		self.top = top
		self.layouts = []
		for pin in self.validPins:
			id = pin
			if id != 0:
				id -= 4
			mask = 0
			if pin != 0:
				mask |= (1 << (pin - 1))
			self.layouts.append( (id, mask) )

	def supportedLayouts(self):
		return self.layouts

	def setLayoutID(self, id):
		self.top.cmdLoadGNDLayout(id)

if __name__ == "__main__":
	print "ZIF socket GND layouts"
	print GNDLayout()
