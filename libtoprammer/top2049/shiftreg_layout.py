"""
#    TOP2049 Open Source programming suite
#
#    TOP2049 Shiftregister based layout definitions
#
#    Copyright (c) 2010 Michael Buesch <mb@bu3sch.de>
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


class ShiftregLayout:
	def __init__(self, nrShiftRegs):
		assert(nrShiftRegs <= 4)
		self.nrShiftRegs = nrShiftRegs
		self.layouts = []
		for id in range(0, len(self.shiftreg_masks)):
			shreg_mask = self.shiftreg_masks[id]
			zif_mask = 0
			for bit in range(0, self.nrShiftRegs * 8):
				if (shreg_mask & (1 << bit)) == 0:
					continue
				regId = self.__bitnr2shregId(bit)
				zifPin = self.shreg2zif_map[regId]
				zif_mask |= (1 << (zifPin - 1))
			if id == 0 or zif_mask != 0:
				self.layouts.append( (id, zif_mask) )

	def __bitnr2shregId(self, bitNr):
		if bitNr >= 24:
			register = 3
			pin = bitNr - 24
		elif bitNr >= 16:
			register = 2
			pin = bitNr - 16
		elif bitNr >= 8:
			register = 1
			pin = bitNr - 8
		else:
			register = 0
			pin = bitNr
		return "%d.%d" % (register, pin)

	def __repr__(self):
		res = ""
		for (id, zif_mask) in self.supportedLayouts():
			res += "Layout %d:\n" % id
			res += "        o---------o\n"
			for pin in range(1, 25):
				left = "     "
				right = ""
				if (1 << (pin - 1)) & zif_mask:
					left = "HOT >"
				if (1 << (49 - pin - 1)) & zif_mask:
					right = "< HOT"
				res += "%s   | %2d | %2d |   %s\n" % (left, pin, 49 - pin, right)
			res += "        o---------o\n\n"
		return res

	def supportedLayouts(self):
		"""Returns a list of supported layouts.
		Each entry is a tuple of (id, bitmask), where bitmask is
		the ZIF layout. bit0 is ZIF-pin-1. A bit set means a hot pin."""
		return self.layouts

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
		for (layoutId, layoutMask) in self.layouts:
			if layoutMask == zifMask:
				self.setLayoutID(layoutId)
				return
		raise TOPException("Layout mask impossible due to hardware constraints")

	def setLayoutID(self, id):
		"Load a specific layout ID."
		# Reimplement me in the subclass
		raise Exception()
