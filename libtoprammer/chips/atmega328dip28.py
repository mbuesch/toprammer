"""
#    TOP2049 Open Source programming suite
#
#    Atmel Mega328 DIP28 support
#
#    Copyright (c) 2009-2015 Michael Buesch <m@bues.ch>
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


class Chip_ATMega328DIP28(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipPackage = "DIP28",
			chipPinVCC = 7,
			chipPinsVPP = 1,
			chipPinGND = 8,
			signature = b"\x1E\x95\x14",
			flashPageSize = 64,
			flashPages = 256,
			eepromPageSize = 4,
			eepromPages = 256,
			fuseBytes = 3)

ChipDescription(
	Chip_ATMega328DIP28,
	bitfile = "atmega8dip28",
	chipID = "atmega328dip28",
	runtimeID = (0x0003, 0x01),
	chipVendors = "Atmel",
	description = "AtMega328",
	packages = ( ("DIP28", ""), ),
)

class Chip_ATMega328pDIP28(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipPackage = "DIP28",
			chipPinVCC = 7,
			chipPinsVPP = 1,
			chipPinGND = 8,
			signature = b"\x1E\x95\x0F",
			flashPageSize = 64,
			flashPages = 256,
			eepromPageSize = 4,
			eepromPages = 256,
			fuseBytes = 3)

ChipDescription(
	Chip_ATMega328pDIP28,
	bitfile = "atmega8dip28",
	chipID = "atmega328pdip28",
	runtimeID = (0x0003, 0x01),
	chipVendors = "Atmel",
	description = "AtMega328P",
	packages = ( ("DIP28", ""), ),
)
