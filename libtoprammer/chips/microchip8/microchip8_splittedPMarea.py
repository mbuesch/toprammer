"""
#    TOP2049 Open Source programming suite
#
#    pic8_splittedPMarea - file for newer 8bit PIC MCUs
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

class microchip8_splittedPMarea(Chip_Microchip8_common):
	CMD_LOAD_CONFIGURATION = 0x00
	
	logicalFlashProgramMemorySize = 0x2000
	logicalFlashConfigurationMemorySize = 0x2000
	   
	CMD_BEGIN_INTERNALLY_TIMED_PROGRAMMING = 0x08
	CMD_BEGIN_EXTERNALLY_TIMED_PROGRAMMING = 0x18
	CMD_END_EXTERNALLY_TIMED_PROGRAMMING = 0x0A
	CMD_ROW_ERASE_PGM = 0x11
	
	delayTinternalProgDM = 0.005
	delayTinternalProgPM = 0.0025
	# overriding: 
	delayTdis = 0.0003
	delayTprog = 0.0021
	delayTdly = 0.0000015
	delayTera = 0.005

	defaultWord = [b'\xFF', b'\x3F']

	def __init__(self,
	    chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
	    signature,
	    flashPageSize, flashPages,
	    eepromPageSize, eepromPages,
	    fuseBytes
	    ):
		Chip_Microchip8_common.__init__(self, chipPackage, chipPinVCC, chipPinsVPP, chipPinGND, signature, flashPageSize, flashPages, eepromPageSize, eepromPages, fuseBytes)
		self.isInsideProgramMemoryArea = True
		self.initPcValue = 0
		self.userIDLocationAddr = self.logicalFlashProgramMemorySize
		self.deviceIDAddr = self.logicalFlashProgramMemorySize + 0x06
		self.configWordAddr = self.logicalFlashProgramMemorySize + 0x07

	def getIHexInterpreter(self):
		inter = IHexInterpreter()
		inter.progmemRanges = [ AddressRange(0, 2 * self.flashPageSize) ]
		inter.fuseRanges = [ AddressRange(2 * self.configWordAddr,
						  2 * self.configWordAddr + 1) ]
		inter.uilRanges = [ AddressRange(2 * self.userIDLocationAddr,
						 2 * (self.userIDLocationAddr + self.userIDLocationSize) - 1) ]
		inter.progmemDefaultBytes = self.defaultWord[0] + self.defaultWord[1]
		inter.fuseDefaultBytes = self.defaultWord[0] + self.defaultWord[1]
		return inter

	def incrementPC(self, count):
		for address in range(0, count):
			self.sendCommand(0, 0, 0, self.CMD_INCREMENT_ADDRESS)
			self.PC += 1
			if(self.isInsideProgramMemoryArea):
				if (self.PC == self.logicalFlashProgramMemorySize):
					self.PC = 0
			else:
				if (self.PC == self.logicalFlashConfigurationMemorySize):
					self.PC = self.logicalFlashProgramMemorySize

	def enterConfigArea(self, wordLatched=0):
		self.send6bitWriteInstruction(self.CMD_LOAD_CONFIGURATION, wordLatched)
		self.PC = self.logicalFlashProgramMemorySize
		self.isInsideProgramMemoryArea = False
	
	def setPC(self, address):
		if(self.isInsideProgramMemoryArea):
			if(address >= self.logicalFlashProgramMemorySize):
				raise(TOPException('Cannot set PC to address inside PM {:x}'.format(address)))
		else:
			if(address < self.logicalFlashProgramMemorySize):
				raise(TOPException('Cannot set PC to address outside PM {:x}'.format(address)))
		while(self.PC != address):
			self.incrementPC(1)
	
	def readSignature(self):
		self.progressMeterInit("Reading signature", 0)
		self.enterPM()
		self.enterConfigArea()
		self.setPC(self.deviceIDAddr)
		idSize = 1
		for i in range(0, idSize):
			self.sendReadFlashInstr()
			self.top.hostDelay(0.00002)
			self.readSDOBufferLow()
			self.readSDOBufferHigh()
			self.incrementPC(1)
		self.progressMeterFinish()
		return self.top.cmdReadBufferReg()[0:2 * idSize]
			
	def sendWriteFlashInstrExternallyTimed(self):
		'''
		'''
		self.sendCommand(0, 0, 0, self.CMD_BEGIN_EXTERNALLY_TIMED_PROGRAMMING)
		self.top.hostDelay(self.delayTprog)
		self.sendCommand(0, 0, 0, self.CMD_END_EXTERNALLY_TIMED_PROGRAMMING)
		self.top.hostDelay(self.delayTdis)
	
	def sendWriteFlashInstrPM(self):
		'''
		'''
		self.sendCommand(0, 0, 0, self.CMD_BEGIN_INTERNALLY_TIMED_PROGRAMMING)
		self.top.hostDelay(self.delayTinternalProgPM)
	
	def sendWriteFlashInstrCW(self):
		'''
		'''
		self.sendCommand(0, 0, 0, self.CMD_BEGIN_INTERNALLY_TIMED_PROGRAMMING)
		self.top.hostDelay(self.delayTinternalProgDM)	
	
	def sendWriteFlashInstr(self):
		'''
		'''
		self.sendWriteFlashInstrPM()
	
	def sendWriteFlashInstrDM(self):
		'''
		'''
		self.sendWriteFlashInstrExternallyTimed()      
