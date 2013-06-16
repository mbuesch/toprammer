"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC12F1822 DIP8
#
#    Copyright (c) 2012 Pavel Stemberk <stemberk@gmail.com>
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

from microchip02_common import *

class Chip_Pic12F1822dip8(Chip_Microchip02_common):
	voltageVDD = 3
	voltageVPP = 8.5
	#CONFIGURATION WORD FOR PIC10F200/202/204/206
	#X X X X   X X X MCLRE     /CP WDT X X
	logicalFlashProgramMemorySize = 0x8000
	logicalFlashConfigurationMemorySize = 0x8000
	rowSize = 16
	nLatches = 16
	userIDLocationSize = 4

    	def __init__(self):
	    	Chip_Microchip02_common.__init__(self,
			chipPackage="DIP8",
			chipPinVCC=1,
			chipPinsVPP=4,
			chipPinGND=8,
			signature="\x08\x27",
			flashPageSize=0x800,
			flashPages=1,
			eepromPageSize=0,
			eepromPages=0,
			fuseBytes=4
			)
		self.configWordAddr = 0x8007
		#self.osccalAddr = 0x2000
		self.userIDLocationAddr = 0x8000
		self.deviceIDAddr = 0x8006
		self.programMemoryByteAddressRange = [(0,2*self.flashPageSize)]
		self.configWordByteAddressRange = [(2*self.configWordAddr,2*self.configWordAddr+self.fuseBytes-1)]
		self.userIDLocationByteAddressRange = [(2*self.userIDLocationAddr, 2*(self.userIDLocationAddr+self.userIDLocationSize)-1)]
 
		#self.osccalBackupAddr = self.userIDLocationAddr + self.userIDLocationSize

fuseDesc = (
    BitDescription(0, "FOSC[0], 0=LP, 100=INTOSC"),
    BitDescription(1, "FOSC[1]"),
    BitDescription(2, "FOSC[2]"),
    BitDescription(3, "WDTE[0], 00=WDT disabled, 11=WDT enabled"),
    BitDescription(4, "WDTE[1]"),
    BitDescription(5, "nPWRTE"),
    BitDescription(6, "MCLRE, 1=nMCLR/Vpp pin is nMCLR, weak pull-up enabled, ignored if LVP=1 "),
    BitDescription(7, "nCP 1=program memory code protection is disabled"),
    BitDescription(8, "nCPD, 1=data memory code protection is disabled"),
    BitDescription(9, "BOREN[0], 00=BOR disabled"),
    BitDescription(10, "BOREN[1]"),
    BitDescription(11, "nCLKOUTEN, 0=CLKOUT is enabled on CLKOUT pin"),
    BitDescription(12, "IESO, 0=Internal/External Switchover mode is disabled"),
    BitDescription(13, "FCMEM, 0=Fail-Safe Clock Monitor is disabled"),
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
    BitDescription(24, "PLLEN, 0=4xPLL disabled"),
    BitDescription(25, "STVREN, 1=Stack overflow or underflow will cause a reset"),
    BitDescription(26, "BORV"),
    BitDescription(27, "Unused"),
    BitDescription(28, "nDEBUG, 0=ICSPCLK and ICSPDAT are dedicated to the debugger"),
    BitDescription(29, "LVP 1=Low-voltage programming enabled"),
)

ChipDescription(
	Chip_Pic12F1822dip8,
	bitfile = "microchip01dip8",
	chipID = "pic12f1822dip8",
	runtimeID = (0xDE02, 0x01),
	chipVendors = "Microchip",
	description = "PIC12F1822, PIC12LF1822",
	packages = (("DIP8", ""),),
	fuseDesc = fuseDesc,	
	maintainer = "Pavel Stemberk <stemberk@gmail.com>",
)
