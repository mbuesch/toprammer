"""
#    TOP2049 Open Source programming suite
#
#    Microchip8 - 18f1220 family - 8bit PIC MCU
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

from libtoprammer.chips.microchip8.microchip8_18_common import *

class microchip8_18f1220family(Chip_Microchip8_18_common):
	
	voltageVDD				 = 4.5
	voltageVPP				 = 9
	
	writeBufferSize				 = 8
	eraseBufferSize				 = 64

	def __init__(self,
			chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
			signature,
			flashPageSize, flashPages,
			eepromPageSize, eepromPages,
			fuseBytes
			):
		Chip_Microchip8_18_common.__init__(self,
		chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
			signature,
			flashPageSize, flashPages,
			eepromPageSize, eepromPages,
			fuseBytes)	

	def erase(self):
		self.progressMeterInit("Erasing chip", 0)
		self.enterPM(True)
		self.executeCode(self.getCodeAddrToTBLPTR(0x3C0004))
		self.send4bitWriteInstruction(self.CMD_TW, 0x0080)
		self.executeCode((0x0000,))
		self.sendCommand(1)		
		self.top.cmdDelay(self.delayP11 + self.delayP10)
		for i in range(0,4):
			self.sendCommand(1)
		self.top.flushCommands()
		self.progressMeterFinish()
	
	def setEEPROMAddr(self, addr):
		self.executeCode((0x0E00 | (addr & 0xFF), 0x6EA9))
