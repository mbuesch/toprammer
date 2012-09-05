"""
#    TOP2049 Open Source programming suite
#
#    Atmel Mega8 DIP28 support
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

from atmega_common import *


class Chip_ATMega8DIP28(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipPackage = "DIP28",
			chipPinVCC = 7,
			chipPinsVPP = 1,
			chipPinGND = 8,
			signature = "\x1E\x93\x07",
			flashPageSize = 32,
			flashPages = 128,
			eepromPageSize = 4,
			eepromPages = 128,
			fuseBytes = 2)

fuseDesc = (
	BitDescription(0, "CKSEL0"),
	BitDescription(1, "CKSEL1"),
	BitDescription(2, "CKSEL2"),
	BitDescription(3, "CKSEL3"),
	BitDescription(4, "SUT0"),
	BitDescription(5, "SUT1"),
	BitDescription(6, "BODEN"),
	BitDescription(7, "BODLEVEL"),
	BitDescription(8, "BOOTRST"),
	BitDescription(9, "BOOTSZ0"),
	BitDescription(10, "BOOTSZ1"),
	BitDescription(11, "EESAVE"),
	BitDescription(12, "CKOPT"),
	BitDescription(13, "SPIEN"),
	BitDescription(14, "WDTON"),
	BitDescription(15, "RSTDISBL"),
)

lockbitDesc = (
	BitDescription(0, "LB1"),
	BitDescription(1, "LB2"),
	BitDescription(2, "BLB01"),
	BitDescription(3, "BLB02"),
	BitDescription(4, "BLB11"),
	BitDescription(5, "BLB12"),
	BitDescription(6, "Unused"),
	BitDescription(7, "Unused"),
	BitDescription(8, "Unused"),
)

ChipDescription(
	Chip_ATMega8DIP28,
	bitfile = "atmega8dip28",
	runtimeID = (0x0003, 0x01),
	chipVendors = "Atmel",
	description = "AtMega8",
	fuseDesc = fuseDesc,
	lockbitDesc = lockbitDesc,
	packages = ( ("DIP28", ""), )
)
