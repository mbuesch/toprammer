"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC16F1507 DIP20
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

from microchip8_splittedPMarea_hasResetPC import *

class Chip_Pic16F1507dip20(microchip8_splittedPMarea_hasResetPC):

	nLatches = 16
	rowSize = 16
	
    	def __init__(self):
	    	microchip8_splittedPMarea_hasResetPC.__init__(self,
			chipPackage="DIP20",
			chipPinVCC=1,
			chipPinsVPP=4,
			chipPinGND=20,
			signature="\x80\x2D",
			flashPageSize=0x800,
			flashPages=1,
			eepromPageSize=256,
			eepromPages=0,
			fuseBytes=4
			)

fuseDesc = (
	BitDescription(0, "FOSC[0], 0=LP, 00=INTOSC"),
	BitDescription(1, "FOSC[1]"),
	BitDescription(2, "Unused"),
	BitDescription(3, "WDTE[0], 00=WDT disabled, 11=WDT enabled"),
	BitDescription(4, "WDTE[1]"),
	BitDescription(5, "nPWRTE"),
	BitDescription(6, "MCLRE, 1=nMCLR/Vpp pin is nMCLR, weak pull-up enabled, ignored if LVP=1 "),
	BitDescription(7, "nCP 1=program memory code protection is disabled"),
	BitDescription(8, "Unused"),
	BitDescription(9, "BOREN[0], 00=BOR disabled"),
	BitDescription(10, "BOREN[1]"),
	BitDescription(11, "nCLKOUTEN, 0=CLKOUT is enabled on CLKOUT pin"),
	BitDescription(12, "Unused"),
	BitDescription(13, "Unused"),
	BitDescription(14, "NA"),
	BitDescription(15, "NA"),
	
	BitDescription(16, "WRT[0], 11=Write protection off"),
	BitDescription(17, "WRT[1]"),
	BitDescription(18, "Unused"),
	BitDescription(19, "Unused"),
	BitDescription(20, "Unused"),
	BitDescription(21, "Unused"),
	BitDescription(22, "Unused"),
	BitDescription(23, "Unused"),
	BitDescription(24, "Unused"),
	BitDescription(25, "STVREN, 1=Stack overflow or underflow will cause a reset"),
	BitDescription(26, "BORV"),
	BitDescription(27, "nLPBOR, 1=Low-Power BOR is disabled"),
	BitDescription(28, "Unused"),
	BitDescription(29, "LVP 1=Low-voltage programming enabled"),
)

ChipDescription(
	Chip_Pic16F1507dip20,
	bitfile="microchip01dip14dip20",
	chipID="pic16F1507dip20",
	runtimeID=(0xDE03, 0x01),
	chipVendors="Microchip",
	description="PIC16F1507, PIC16LF1507",
	packages=(("DIP20", ""),),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
