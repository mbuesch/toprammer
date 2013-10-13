"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC24f04ka200 DIP18
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

from microchip16_common import *

class Chip_Pic24f04ka200dip14(Chip_Microchip16_common):
	
	voltageVDD = 3
	voltageVPP = 7.75
	
	logicalFlashProgramMemorySize = 0x800000
	logicalFlashConfigurationMemorySize = 0x800000	
	
	def __init__(self):
	 	Chip_Microchip16_common.__init__(self,
		chipPackage="DIP14",
		chipPinVCC=14,
		chipPinsVPP=1,
		chipPinGND=13,
		signature="\x02\x84",
		flashPageSize=0x200,
		flashPages=1,
		eepromPageSize=64,
		eepromPages=1,
		fuseBytes=16 * 2
		)
		self.configWordAddr = 0xF80000
		# self.osccalBackupAddr = self.userIDLocationAddr + self.userIDLocationSize

	def getIHexInterpreter(self):
		inter = IHexInterpreter()
		inter.progmemRanges = [ AddressRange(0, 2 * self.flashPageSize) ]
		inter.fuseRanges = [ AddressRange(2 * self.configWordAddr,
						  2 * self.configWordAddr + 1) ]
		return inter

	def sendWriteFlashInstr(self):
		'''
		'''
		self.sendInstr(self.CMD_BEGIN_PROGRAMMING_ONLY_CYCLE)
		self.top.hostDelay(self.delayTinternalProgDM)
	
fuseDesc = (
	BitDescription(0, "FOSC[0], 00=LP osc, 01=XT osc"),
	BitDescription(1, "FOSC[1], 10=HS osc, 11=RC osc"),
	BitDescription(2, "WDTEN, 1=WDT enabled"),
	BitDescription(3, "nPWRT"),
	BitDescription(4, "nCP"),
	BitDescription(5, "nCP"),
	BitDescription(6, "nCP"),
	BitDescription(7, "nCP"),
	BitDescription(8, "nCP"),
	BitDescription(9, "nCP"),
	BitDescription(10, "nCP"),
	BitDescription(11, "nCP"),
	BitDescription(12, "nCP"),
	BitDescription(13, "nCP"),
)

ChipDescription(
	Chip_Pic24f04ka200dip14,
	bitfile="microchip16dip14dip20",
	chipID="pic24f04ka200dip14",
	runtimeID=(0xDF01, 0x01),
	chipVendors="Microchip",
	description="PIC24F04KA200 - experimental mode !!!",
	packages=(("DIP14", ""),),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
