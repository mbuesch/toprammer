"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC10F200, PIC10F204 and PI10f220  DIP8
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

from microchip01_common import *


class Chip_Pic10F200dip8(Chip_Microchip01_common):
    voltageVDD = 5
    voltageVPP =13
    #CONFIGURATION WORD FOR PIC10F200/202/204/206
    #X X X X   X X X MCLRE     /CP WDT X X
    logicalFlashSize = 0x200
    userIDLocationSize = 4
    SUPPORT_SIGREAD		= (0 << 1)
    

    def __init__(self):
        Chip_Microchip01_common.__init__(self,
                  chipPackage = "DIP8",
                  chipPinVCC = 2,
                  chipPinsVPP = 8,
                  chipPinGND = 7,
                  signature = "\x09\x18\x24\x35",
                  flashPageSize = 0x100,
                  flashPages = 1,
                  eepromPageSize = 0,
                  eepromPages = 0,
                  fuseBytes = 2
                  )
        self.configWordAddr = self.logicalFlashSize-1
        self.osccalAddr = self.flashPageSize-1
        self.userIDLocationAddr = self.flashPageSize
        self.osccalBackupAddr = self.userIDLocationAddr + self.userIDLocationSize
        self.programMemoryByteAddressRange = [(0,2*self.flashPageSize)]
        self.configWordByteAddressRange = [(2*self.configWordAddr,2*self.configWordAddr+1), (2*0xFFF, 2*0xFFF+1)]
        self.userIDLocationByteAddressRange = [(2*self.userIDLocationAddr, 2*(self.userIDLocationAddr+self.userIDLocationSize)-1)]
        
    
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
	Chip_Pic10F200dip8,
	bitfile = "pic10fxxxdip8",
	chipID = "pic10f200dip8",
	runtimeID = (0xDE01, 0x01),
	chipVendors = "Microchip",
	description = "PIC10F200, PIC10F204, PIC10F220",
	packages = ( ("DIP8", ""), ),
	fuseDesc = fuseDesc,
	maintainer = "Pavel Stemberk <stemberk@gmail.com>",
)
