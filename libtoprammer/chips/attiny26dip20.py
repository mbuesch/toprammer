"""
#    TOP2049 Open Source programming suite
#
#    Atmel Tiny26 DIP20 support
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


class Chip_ATTiny26DIP20(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipPackage = "DIP20",
			chipPinVCC = 5,
			chipPinsVPP = 10,
			chipPinGND = 6,
			signature = "\x1E\x91\x09",
			flashPageSize = 16,
			flashPages = 64,
			eepromPageSize = 4,
			eepromPages = 32,
			fuseBytes = 2)

ChipDescription(
	Chip_ATTiny26DIP20,
	bitfile = "attiny26dip20",
	runtimeID = (0x0002, 0x01),
	chipVendors = "Atmel",
	description = "AtTiny26",
	packages = ( ("DIP20", ""), ),
	comment = "Special ZIF position",
	broken = True
)
