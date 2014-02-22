#
# THIS FILE WAS AUTOGENERATED BY makeSip6.py
# Do not edit this file manually. All changes will be lost.
#

"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC24f04kl101 SIP6
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

from microchip16_common import *
from configWords import klx0x_fuseDesc

class Chip_Pic24f04kl101sip6(Chip_Microchip16_common):
	
	voltageVDD = 3.3
	voltageVPP = 8
	
	logicalFlashProgramMemorySize = 0x800000
	logicalFlashConfigurationMemorySize = 0x800000
	
	hasEEPROM = False
	
	def __init__(self):
	 	Chip_Microchip16_common.__init__(self,
		chipPackage = "DIP10",
		chipPinVCC = 9,
		chipPinsVPP = 10,
		chipPinGND = 8,
		signature="\x02\x4b",
		# flashPageSize (in number of 24bit words)
		flashPageSize=0xAFE / 2 + 2,
		# flashPageSize=0x40,
		flashPages=1,
		# eepromPageSize (in 16bit words)
		eepromPageSize=0,
		eepromPages=0,
		# all 7 words uses lowest byte only
		fuseBytes=2 * 9
		)
		self.configWordAddr = 0xF80000
		# self.osccalBackupAddr = self.userIDLocationAddr + self.userIDLocationSize

fuseDesc = klx0x_fuseDesc

ChipDescription(
	Chip_Pic24f04kl101sip6,
	bitfile = "microchip16sip6",
	chipID="pic24f04kl101sip6",
	runtimeID = (0xDF05, 0x01),
	chipVendors="Microchip",
	description = "PIC24F04KL101 - ICD",
	packages = (("DIP10", ""), ),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
