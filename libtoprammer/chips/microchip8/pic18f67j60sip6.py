"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC18F67J60 SIP6
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

from microchip8_18f97j60family import *

class Chip_PIC18F67J60sip6(microchip8_18f97j60family):

	hasEEPROM = True

     	writeBufferSize			 = 8
     	eraseBufferSize			 = 64
     	
     	def __init__(self):
     		microchip8_18f97j60family.__init__(self,
			chipPackage="DIP10",
			chipPinVCC=9,
			chipPinsVPP=10,
			chipPinGND=8,
			signature="\x22\x21",
			flashPageSize=0x2000,
			flashPages=1,
			eepromPageSize=0x100,
			eepromPages=1,
			fuseBytes=6
			)
			

fuseDesc = (
	BitDescription(0o00, "WDTEN"),
	BitDescription(0o01, "NA"),
	BitDescription(0o02, "NA"),
	BitDescription(0o03, "NA"),
	BitDescription(0o04, "NA"),
	BitDescription(0o05, "STVREN"),
	BitDescription(0o06, "XINST"),
	BitDescription(0o07, "nDEBUG"),
	BitDescription(0o10, "NA"),
	BitDescription(0o11, "NA"),
	BitDescription(0o12, "CP[0]"),
	BitDescription(0o13, "NA"),
	BitDescription(0o14, "NA"),
	BitDescription(0o15, "NA"),
	BitDescription(0o16, "NA"),
	BitDescription(0o17, "NA"),
    
	BitDescription(0o20, "FOSC[0]"),
	BitDescription(0o21, "FOSC[1]"),
	BitDescription(0o22, "FOSC[2]"),
	BitDescription(0o23, "NA"),
	BitDescription(0o24, "NA"),
	BitDescription(0o25, "NA"),
	BitDescription(0o26, "FCMEN, 0=Fail-Safe Clock Monitor is disabled"),
	BitDescription(0o27, "IESO, 0=Internal/External Switchover mode is disabled"),
	BitDescription(0o30, "WDTPS[0]"),
	BitDescription(0o31, "WDTPS[1]"),
	BitDescription(0o32, "WDTPS[2]"),
	BitDescription(0o33, "WDTPS[3]"),
	BitDescription(0o34, "NA"),
	BitDescription(0o35, "NA"),
	BitDescription(0o36, "NA"),
	BitDescription(0o37, "NA"),
	
	BitDescription(0o40, "NA"),
	BitDescription(0o41, "NA"),
	BitDescription(0o42, "NA"),
	BitDescription(0o43, "NA"),
	BitDescription(0o44, "NA"),
	BitDescription(0o45, "NA"),
	BitDescription(0o46, "NA"),
	BitDescription(0o47, "NA"),
	BitDescription(0o50, "NA"),
	BitDescription(0o51, "NA"),
	BitDescription(0o52, "NA"),
	BitDescription(0o53, "NA"),
	BitDescription(0o54, "NA"),
	BitDescription(0o55, "ETHLED"),
	BitDescription(0o56, "NA"),
	BitDescription(0o57, "NA"),
)

ChipDescription(
	Chip_PIC18F67J60sip6,
	bitfile="microchip01sip6",
	chipID="PIC18F67J60sip6",
	runtimeID=(0xDE05, 0x01),
	chipVendors="Microchip",
	description="PIC18F67J60",
	packages=(("sip6", ""),),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
