"""
#    TOP2049 Open Source programming suite
#
#    Microchip8 - 18f2221 family - 8bit PIC MCU
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

class microchip8_18f2221family(Chip_Microchip8_18_common):
	
	voltageVDD				 = 5
	voltageVPP				 = 11
	
	delayP2A = 0.0000008  # Serial clock low time 
	delayP5 = 0.0000015  # Delay between 4-bit command and command operand
  	
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
		self.executeCode(self.getCodeAddrToTBLPTR(0x3C0005))
		self.send4bitWriteInstruction(self.CMD_TW, 0x3F3F)
		self.executeCode(self.getCodeAddrToTBLPTR(0x3C0004))
		self.send4bitWriteInstruction(self.CMD_TW, 0x8F8F)
		self.executeCode((0x0000,))
		self.sendCommand(1)		
		self.top.hostDelay(self.delayP11 + self.delayP10)
		for i in range(0,4):
			self.sendCommand(1)
		self.top.flushCommands()
		self.progressMeterFinish()
	
	def eraseRow(self, rowAddr):
		self.executeCode((0x8EA6, 0x9CA6, 0x84A6))
		self.executeCode(self.getCodeAddrToTBLPTR(rowAddr))
		self.executeCode((0x88A6, 0x82A6))
		self.sendCommand(1, 0, 0, 0x0, 1)
		self.top.hostDelay(self.delayP9)
		self.setPins(0)
		self.top.hostDelay(self.delayP10)	

	def setEEPROMAddr(self, addr):
		self.executeCode((0x0E00 | (addr & 0xFF), 0x6EA9, (0x0E00 | ((addr >> 8) & 0xFF)), 0x6EAA))
			
