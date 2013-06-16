"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC16F59 SIP6
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

from microchip01_common import *


class Chip_Pic16F59sip6(Chip_Microchip01_common):
    voltageVDD = 5
    voltageVPP =13
    #CONFIGURATION WORD FOR PIC10F200/202/204/206
    #X X X X   X X X MCLRE     /CP WDT X X
    logicalFlashSize = 0x1000
    userIDLocationSize = 4
    SUPPORT_SIGREAD		= (0 << 1)
    

    def __init__(self):
        Chip_Microchip01_common.__init__(self,
                  chipPackage = "DIP10",
                  chipPinVCC = 9,
                  chipPinsVPP = 10,
                  chipPinGND = 8,
                  signature = "",
                  flashPageSize = 0x200,
                  flashPages = 4,
                  eepromPageSize = 0,
                  eepromPages = 0,
                  fuseBytes = 2
                  )
        self.configWordAddr = self.logicalFlashSize-1
        self.userIDLocationAddr = self.flashPageSize
        self.programMemoryByteAddressRange = [(0,2*self.flashPageSize)]
        self.configWordByteAddressRange = [(2*self.configWordAddr,2*self.configWordAddr+self.fuseBytes-1)]
        self.userIDLocationByteAddressRange = [(2*self.userIDLocationAddr, 2*(self.userIDLocationAddr+self.userIDLocationSize)-1)]
        
    
fuseDesc = (
    BitDescription(0, "FOSC0"),
    BitDescription(1, "FOSC1 - 00=LP, 01=XT, 10=HS, 11=RC"),
    BitDescription(2, "WDTE"),
    BitDescription(3, "!CP"),
    BitDescription(4, "Unused"),
    BitDescription(5, "Unused"),
    BitDescription(6, "Unused"),
    BitDescription(7, "Unused"),
    BitDescription(8, "Unused"),
    BitDescription(9, "Unused"),
    BitDescription(10, "Unused"),
    BitDescription(11, "Unused"),
)

ChipDescription(
	Chip_Pic16F59sip6,
	bitfile = "microchip01sip6",
	chipID = "pic16f59sip6",
	runtimeID = (0xDE05, 0x01),
	chipVendors = "Microchip",
	description = "PIC16F59",
	packages = ( ("DIP10", ""), ),
	fuseDesc = fuseDesc,
	maintainer = "Pavel Stemberk <stemberk@gmail.com>",
)
