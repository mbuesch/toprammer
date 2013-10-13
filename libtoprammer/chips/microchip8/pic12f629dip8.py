"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC12F629 DIP8
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

from microchip8_splittedPMarea import *

class Chip_Pic12F629dip8(microchip8_splittedPMarea):
	voltageVDD = 5
	voltageVPP = 9
	
	userIDLocationSize = 4
	hasEEPROM = True

	CMD_BEGIN_INTERNALLY_TIMED_PROGRAMMING = 0x08
	delayTinternalProgPM = 0.002
	delayTinternalProgDM = 0.005
	
    	def __init__(self):
	    	microchip8_splittedPMarea.__init__(self,
			chipPackage="DIP8",
			chipPinVCC=1,
			chipPinsVPP=4,
			chipPinGND=8,
			signature="\xCB\x0F",
			flashPageSize=0x400,  # 1024 words
			flashPages=1,
			eepromPageSize=128,
			eepromPages=1,
			fuseBytes=2
			)
		self.configWordAddr = 0x2007
		self.osccalAddr = self.flashPageSize - 1

fuseDesc = (
	BitDescription(0, "FOSC[0], 0=LP, 100=INTOSC"),
	BitDescription(1, "FOSC[1]"),
	BitDescription(2, "FOSC[2]"),
	BitDescription(3, "WDTE, 0=WDT disabled, 1=WDT enabled"),
	BitDescription(4, "nPWRTE"),
	BitDescription(5, "MCLRE"),
	BitDescription(6, "BODEN, 0=BOD disabled"),
	BitDescription(7, "nCP 1=program memory code protection is disabled"),
	BitDescription(8, "nCPD, 1=data memory code protection is disabled"),
	BitDescription(9, "Unused"),
	BitDescription(10, "Unused"),
	BitDescription(11, "Unused"),
	BitDescription(12, "BG[0], Band Gap Calibration bits, 00 = Lowest band gap voltage"),
	BitDescription(13, "BG[1]"),
)

ChipDescription(
	Chip_Pic12F629dip8,
	bitfile="microchip01dip8",
	chipID="pic12F629dip8",
	runtimeID=(0xDE02, 0x01),
	chipVendors="Microchip",
	description="PIC12F629, PIC12F675",
	packages=(("DIP8", ""),),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
