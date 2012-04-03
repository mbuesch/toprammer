"""
#    TOP2049 Open Source programming suite
#
#    TOP2049 Shiftregister based layout definitions
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

from libtoprammer.generic_layout import *


class ShiftregLayout(GenericLayout):
	def __init__(self, nrZifPins, nrShiftRegs):
		GenericLayout.__init__(self, nrZifPins)
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
		register = bitNr // 8
		pin = bitNr % 8
		return "%d.%d" % (register, pin)

	def supportedLayouts(self):
		return self.layouts
