"""
#    TOP2049 Open Source programming suite
#
#    Atmel Mega48 DIP28 support
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


class Chip_ATMega48DIP28(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipPackage = "DIP28",
			chipPinVCC = 7,
			chipPinsVPP = 1,
			chipPinGND = 8,
			signature = b"\x1E\x92\x05",
			flashPageSize = 32,
			flashPages = 64,
			eepromPageSize = 4,
			eepromPages = 64,
			fuseBytes = 3)

ChipDescription(
	Chip_ATMega48DIP28,
	bitfile = "atmega8dip28",
	chipID = "atmega48dip28",
	runtimeID = (0x0003, 0x01),
	chipVendors = "Atmel",
	description = "AtMega48",
	packages = ( ("DIP28", ""), ),
)

class Chip_ATMega48pDIP28(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipPackage = "DIP28",
			chipPinVCC = 7,
			chipPinsVPP = 1,
			chipPinGND = 8,
			signature = b"\x1E\x92\x0A",
			flashPageSize = 32,
			flashPages = 64,
			eepromPageSize = 4,
			eepromPages = 64,
			fuseBytes = 3)

ChipDescription(
	Chip_ATMega48pDIP28,
	bitfile = "atmega8dip28",
	chipID = "atmega48pdip28",
	runtimeID = (0x0003, 0x01),
	chipVendors = "Atmel",
	description = "AtMega48P",
	packages = ( ("DIP28", ""), ),
)
