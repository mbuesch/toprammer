"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC24f08kl302 DIP28
#
#    Copyright (c) 2014 Pavel Stemberk <stemberk@gmail.com>
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

from .microchip16_common import *
from .configWords import klx0x_fuseDesc

class Chip_Pic24f08kl302dip28(Chip_Microchip16_common):
	
	voltageVDD = 3.3
	voltageVPP = 8
	
	logicalFlashProgramMemorySize = 0x800000
	logicalFlashConfigurationMemorySize = 0x800000
	
	eepromStartAddress = 0x7FFF00
	
	def __init__(self):
		Chip_Microchip16_common.__init__(self,
			chipPackage="DIP28",
			chipPinVCC=28,
			chipPinsVPP=1,
			chipPinGND=27,
			signature=b"\x00\x4b",
			# flashPageSize (in number of 24bit words)
			flashPageSize=0x15fe // 2 + 2,
			# flashPageSize=0x40,
			flashPages=1,
			# eepromPageSize (in 16bit words)
			eepromPageSize=0x80,
			eepromPages=1,
			# all 7 words uses lowest byte only
			fuseBytes=2 * 9
		)
		self.configWordAddr = 0xF80000
		# self.osccalBackupAddr = self.userIDLocationAddr + self.userIDLocationSize

fuseDesc = klx0x_fuseDesc

ChipDescription(
	Chip_Pic24f08kl302dip28,
	bitfile="microchip16dip28",
	chipID="pic24f08kl302dip28",
	runtimeID=(0xDF02, 0x01),
	chipVendors="Microchip",
	description="PIC24F08KL302",
	packages=(("DIP28", ""),),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
