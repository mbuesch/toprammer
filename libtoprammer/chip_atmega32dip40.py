"""
#    TOP2049 Open Source programming suite
#
#    Atmel Mega32 DIP40 support
#
#    Copyright (c) 2009-2010 Michael Buesch <mb@bu3sch.de>
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

from chip_atmega_common import *

# Note: Chip has to be inserted upside-down into the ZIF

class Chip_ATMega32DIP40(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipID = "atmega32dip40",
			chipPackage = "DIP40",
			chipPinVCCX = 10,
			chipPinVPP = 9,
			chipPinGND = 11,
			signature = "\x1E\x95\x02",
			presenceCheckLayout = 0x0043FF000000,
			flashPageSize = 64,
			flashPages = 256,
			eepromPageSize = 4,
			eepromPages = 256)

supportedChips.append(Chip_ATMega32DIP40())
