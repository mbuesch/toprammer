"""
#    TOP2049 Open Source programming suite
#
#    Generic ZIF socket voltage layout
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

from libtoprammer.util import *


class GenericLayout:
	def __init__(self, nrZifPins):
		self.nrZifPins = nrZifPins

	def getNrOfPins(self):
		"Returns the number of pins on the layout"
		return self.nrZifPins

	def __repr__(self):
		res = ""
		for (id, zif_mask) in self.supportedLayouts():
			res += "Layout %d:\n" % id
			res += "        o---------o\n"
			for pin in range(1, self.nrZifPins // 2 + 1):
				left = "     "
				right = ""
				if (1 << (pin - 1)) & zif_mask:
					left = "HOT >"
				if (1 << (self.nrZifPins - pin)) & zif_mask:
					right = "< HOT"
				res += "%s   | %2d | %2d |   %s\n" % \
					(left, pin, self.nrZifPins + 1 - pin, right)
			res += "        o---------o\n\n"
		return res

	def supportedLayouts(self):
		"""Returns a list of supported layouts.
		Each entry is a tuple of (id, bitmask), where bitmask is
		the ZIF layout. bit0 is ZIF-pin-1. A bit set means a hot pin."""
		# Reimplement me in the subclass
		raise Exception()

	def ID2mask(self, id):
		"Convert a layout ID to a layout mask"
		for (layoutId, layoutMask) in self.supportedLayouts():
			if id == layoutId:
				return layoutMask
		return None

	def ID2pinlist(self, id):
		"Convert a layout ID to a list of pins"
		pinlist = []
		mask = self.ID2mask(id)
		for i in range(0, self.nrZifPins):
			if mask & (1 << i):
				pinlist.append(i + 1)
		return pinlist

	def setLayoutPins(self, zifPinsList):
		"""Load a layout. zifPinsList is a list of hot ZIF pins.
		The first ZIF pin is 1."""
		zifMask = 0
		for zifPin in zifPinsList:
			assert(zifPin >= 1)
			zifMask |= (1 << (zifPin - 1))
		self.setLayoutMask(zifMask)

	def setLayoutMask(self, zifMask):
		"Load a ZIF mask."
		for (layoutId, layoutMask) in self.supportedLayouts():
			if layoutMask == zifMask:
				self.setLayoutID(layoutId)
				return
		raise TOPException("Layout mask impossible due to hardware constraints")

	def setLayoutID(self, id):
		"Load a specific layout ID."
		# Reimplement me in the subclass
		raise Exception()
