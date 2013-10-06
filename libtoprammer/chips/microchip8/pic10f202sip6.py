"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC10F202, PIC10F206 and PIC10f222 DIP8
#
#    Copyright (c) 2013 Pavel Stemberk <stemberk@gmail.com>
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

from microchip8_singlePMarea import *

class Chip_Pic10F202sip6(microchip8_singlePMarea):

	# CONFIGURATION WORD FOR PIC10F200/202/204/206
	# X X X X   X X X MCLRE     /CP WDT X X
	logicalFlashSize = 0x400

	def __init__(self):
		microchip8_singlePMarea.__init__(self,
			chipPackage = "DIP10",
			chipPinVCC = 9,
			chipPinsVPP = 10,
			chipPinGND = 8,
			signature="\x09\x18\x24\x35",
			flashPageSize=0x200,
			flashPages=1,
			eepromPageSize=0,
			eepromPages=0,
			fuseBytes=2
			)
 

fuseDesc = (
	BitDescription(0, "Unused"),
	BitDescription(1, "Unused"),
	BitDescription(2, "WDTE"),
	BitDescription(3, "!CP"),
	BitDescription(4, "MCLRE"),
	BitDescription(5, "Unused"),
	BitDescription(6, "Unused"),
	BitDescription(7, "Unused"),
	BitDescription(8, "Unused"),
	BitDescription(9, "Unused"),
	BitDescription(10, "Unused"),
	BitDescription(11, "Unused"),
)

ChipDescription(
	Chip_Pic10F202sip6,
	bitfile = "microchip01sip6",
	chipID="pic10f202sip6",
	runtimeID = (0xDE05, 0x01),
	chipVendors="Microchip",
	description = "PIC10F202, PIC10F206, PIC10F222 - ICD",
	packages = (("DIP10", ""), ),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
