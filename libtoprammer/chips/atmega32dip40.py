"""
#    TOP2049 Open Source programming suite
#
#    Atmel Mega32 DIP40 support
#
#    Copyright (c) 2009-2010 Michael Buesch <m@bues.ch>
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

from .atmega_common import *


class Chip_ATMega32DIP40(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipPackage = "DIP40",
			chipPinVCC = 10,
			chipPinsVPP = 9,
			chipPinGND = 11,
			signature = b"\x1E\x95\x02",
			flashPageSize = 64,
			flashPages = 256,
			eepromPageSize = 4,
			eepromPages = 256,
			fuseBytes = 2)

ChipDescription(
	Chip_ATMega32DIP40,
	bitfile = "atmega32dip40",
	runtimeID = (0x0004, 0x01),
	chipVendors = "Atmel",
	description = "AtMega32",
	packages = ( ("DIP40", ""), ),
	comment = "Insert upside down into ZIF socket"
)
