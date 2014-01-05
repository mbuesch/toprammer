"""
#    TOP2049 Open Source programming suite
#
#    pic8_singlePMarea - file for older 8bit PIC MCUs
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

from libtoprammer.chips.microchip8.microchip8_common import *

class microchip8_singlePMarea(Chip_Microchip8_common):
	CMD_BEGIN_PROGRAMMING = 0x08
	CMD_END_PROGRAMMING = 0x0E

	userIDLocationSize = 4
	hasSigBytes = False

	voltageVDD = 5
	voltageVPP = 13
	defaultWord = [b'\xFF', b'\x0F']

	def __init__(self,
	    chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
	    signature,
	    flashPageSize, flashPages,
	    eepromPageSize, eepromPages,
	    fuseBytes
	    ):
		Chip_Microchip8_common.__init__(self, chipPackage, chipPinVCC, chipPinsVPP, chipPinGND, signature, flashPageSize, flashPages, eepromPageSize, eepromPages, fuseBytes)
		self.initPcValue		 = self.logicalFlashSize - 1
		self.configWordAddr = self.logicalFlashSize - 1
		self.osccalAddr = self.flashPageSize - 1
		self.userIDLocationAddr = self.flashPageSize
		self.osccalBackupAddr = self.userIDLocationAddr + self.userIDLocationSize

	def getIHexInterpreter(self):
		inter = IHexInterpreter()
		inter.progmemRanges = [ AddressRange(0, 2 * self.flashPageSize) ]
		inter.fuseRanges = [ AddressRange(2 * self.configWordAddr,
						  2 * self.configWordAddr + 1),
				     AddressRange(2 * 0xFFF,
						  2 * 0xFFF + 1) ]
		inter.uilRanges = [ AddressRange(2 * self.userIDLocationAddr,
						 2 * (self.userIDLocationAddr + self.userIDLocationSize) - 1) ]
		inter.progmemDefaultBytes = self.defaultWord[0] + self.defaultWord[1]
		inter.fuseDefaultBytes = self.defaultWord[0] + self.defaultWord[1]
		return inter

	def setPC(self, address):
		while(self.PC != address):
			self.incrementPC(1)
		
	def incrementPC(self, count):
		for address in range(0, count):
			self.sendCommand(0, 0, 0, self.CMD_INCREMENT_ADDRESS)
			self.PC += 1
			if (self.PC == self.logicalFlashSize):
				self.PC = 0
    
	def sendWriteFlashInstr(self):
		'''
		'''
		# self.loadCommand(self.PROGCMD_SENDDATA)
		# self.top.hostDelay(0.000005)
		self.sendCommand(0, 0, 0, self.CMD_BEGIN_PROGRAMMING)
		self.top.cmdDelay(self.delayTprog)  # 025) #Tprog
		self.sendCommand(0, 0, 0, self.CMD_END_PROGRAMMING)
		self.top.cmdDelay(self.delayTdis)  # Tdis
    
	def sendWriteFlashInstrDM(self):
		self.sendWriteFlashInstr()

	def sendWriteFlashInstrCW(self):
		self.sendWriteFlashInstr()
	def readProgmem(self):
		self.exitPM()
		return Chip_Microchip8_common.readProgmem(self)
	def readFuse(self):
		self.exitPM()
		return Chip_Microchip8_common.readFuse(self)
	def writeFuse(self, image):
		self.exitPM()
		Chip_Microchip8_common.writeFuse(self,image)
