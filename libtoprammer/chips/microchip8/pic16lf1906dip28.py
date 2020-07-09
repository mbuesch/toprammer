"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC16LF1906 dip28
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

from .microchip8_splittedPMarea_hasResetPC import *

class Chip_Pic16LF1906dip28(microchip8_splittedPMarea_hasResetPC):
		
	nLatches = 8	

	def __init__(self):
		microchip8_splittedPMarea_hasResetPC.__init__(self,
			chipPackage="dip28",
			chipPinVCC=20,
			chipPinsVPP=1,
			chipPinGND=19,
			signature=b"\x22\x2c",
			flashPageSize=0x2000,
			flashPages=1,
			eepromPageSize=0,
			eepromPages=0,
			fuseBytes=4
			)

fuseDesc = (
	BitDescription(0, "FOSC[0], 00=INTOSC, 11=ECH - High power mode"),
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
	BitDescription(27, "nULPBOR, 1= Ultra low-power BOR is disabled"),
	BitDescription(28, "nDEBUG, 0=ICSPCLK and ICSPDAT are dedicated to the debugger"),
	BitDescription(29, "LVP 1=Low-voltage programming enabled"),
	BitDescription(30, "NA"),
	BitDescription(31, "NA"),
)

ChipDescription(
	Chip_Pic16LF1906dip28,
	bitfile="microchip01dip28",
	chipID="pic16lf1906dip28",
	runtimeID=(0xDE07, 0x01),
	chipVendors="Microchip",
	description="PIC16LF1906",
	packages=(("dip28", ""),),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
