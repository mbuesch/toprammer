"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC12F508 DIP8
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

class Chip_Pic12F508dip8(microchip8_singlePMarea):

	logicalFlashSize = 0x400

	def __init__(self):
		microchip8_singlePMarea.__init__(self,
		chipPackage="DIP8",
		chipPinVCC=1,
		chipPinsVPP=4,
		chipPinGND=8,
		signature="",
		flashPageSize=0x200,
		flashPages=1,
		eepromPageSize=0,
		eepromPages=0,
		fuseBytes=2
		)
	
fuseDesc = (
	BitDescription(0, "FOSC[0] 00=LP, 01=XT, 10=INTOSC, 11=EXTRC"),
	BitDescription(1, "FOSC[1]"),
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
	Chip_Pic12F508dip8,
	bitfile="microchip01dip8",
	chipID="pic12f508dip8",
	runtimeID=(0xDE02, 0x01),
	chipVendors="Microchip",
	description="PIC12F508",
	fuseDesc=fuseDesc, 	
	packages=(("DIP8", ""),),
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
