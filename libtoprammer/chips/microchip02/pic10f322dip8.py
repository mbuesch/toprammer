"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC10F322 DIP8
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

from microchip02_common import *

class Chip_Pic10F322dip8(Chip_Microchip02_common):
	voltageVDD = 3
	voltageVPP = 8.5
	#CONFIGURATION WORD FOR PIC10F200/202/204/206
	#X X X X   X X X MCLRE     /CP WDT X X
	logicalFlashProgramMemorySize = 0x2000
	logicalFlashConfigurationMemorySize = 0x2000
	userIDLocationSize = 4
	rowSize = 32
	nLatches = 16

    	def __init__(self):
	    	Chip_Microchip02_common.__init__(self,
			chipPackage="DIP8",
			chipPinVCC=2,
			chipPinsVPP=8,
			chipPinGND=7,
			signature="\x02\x84",
			flashPageSize=0x200,
			flashPages=1,
			eepromPageSize=0,
			eepromPages=0,
			fuseBytes=2
			)
		self.configWordAddr = 0x2007
		#self.osccalAddr = 0x2000
		self.userIDLocationAddr = 0x2000
		self.deviceIDAddr = 0x2006
		self.programMemoryByteAddressRange = [(0,2*self.flashPageSize)]
		self.configWordByteAddressRange = [(2*self.configWordAddr,2*self.configWordAddr+1)]
		self.userIDLocationByteAddressRange = [(2*self.userIDLocationAddr, 2*(self.userIDLocationAddr+self.userIDLocationSize)-1)]
 
		#self.osccalBackupAddr = self.userIDLocationAddr + self.userIDLocationSize

fuseDesc = (
    BitDescription(0, "FOSC, 1=CLKIN, 0=internal"),
    BitDescription(1, "BOREN[0]"),
    BitDescription(2, "BOREN[1]"),
    BitDescription(3, "WDTE[0]"),
    BitDescription(4, "WDTE[1]"),
    BitDescription(5, "nPWRTE"),
    BitDescription(6, "MCLRE, 1=RA3 is nMCLR, weak pull-up enabled"),
    BitDescription(7, "nCP"),
    BitDescription(8, "LVP"),
    BitDescription(9, "LPBOREN"),
    BitDescription(10, "BORV"),
    BitDescription(11, "WRT[0]"),
    BitDescription(12, "WRT[1] 11=write protection off"),
    BitDescription(13, "Unused"),
)

ChipDescription(
	Chip_Pic10F322dip8,
	bitfile = "pic10fxxxdip8",
	chipID = "pic10f322dip8",
	runtimeID = (0xDE01, 0x01),
	chipVendors = "Microchip",
	description = "PIC10F322, PIC10LF322",
	packages = (("DIP8", ""),),
	fuseDesc = fuseDesc,	
	maintainer = "Pavel Stemberk <stemberk@gmail.com>",
)
