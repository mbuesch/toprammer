"""
#    TOP2049 Open Source programming suite
#
#    Atmel Mega88 DIP28 support
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


class Chip_ATMega88DIP28(Chip_ATMega_common):
	def __init__(self):
		Chip_ATMega_common.__init__(self,
			chipID = "atmega88dip28",
			chipPackage = "DIP28",
			chipPinVCCX = 7,
			chipPinVPP = 1,
			chipPinGND = 8,
			signature = "\x1E\x93\x0A",
			presenceCheckLayout = 0x00031F801000,
			flashPageSize = 32,
			flashPages = 128,
			eepromPageSize = 4,
			eepromPages = 128)

supportedChips.append(Chip_ATMega88DIP28())
