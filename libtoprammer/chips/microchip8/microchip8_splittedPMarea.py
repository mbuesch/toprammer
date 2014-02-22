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
	nDeviceIdRevisionBits = 5
	
	deviceIdMapDict = {
			0o474:"16F1826", 0o475:"16F1827", 0o504:"16LF1826", 0o505:"16LF1827", 0o471:"16F1823", 0o501:"16LF1823",
			0o470:"16F1822", 0o500:"16LF1822", 0o472:"16F1824", 0o502:"16LF1824", 0o473:"16F1825", 0o503:"16LF1825",
			0o476:"16F1828", 0o506:"16LF1828", 0o477:"16F1829", 0o507:"16LF1829",
			0o515:"10F320", 0o514:"10F322", 0o517:"10LF320", 0o516:"10LF322",
			0o174:"12F629", 0o176:"12F675", 0o206:"16F630", 0o207:"16F676",
			0o053:"16F84A",
			0o546:"12F1501", 0o554:"12LF1501", 0o547:"16F1503", 0o555:"16LF1503", 0o550:"16F1507", 0o556:"16LF1507",
			0o551:"16F1508", 0o557:"16LF1508", 0o552:"16F1509", 0o560:"16LF1509",
			0o460:"16F1933", 0o432:"16F1934", 0o433:"16F1936", 0o434:"16F1937", 0o435:"16F1938", 0o436:"16F1939",
			0o450:"16F1946", 0o451:"16F1947", 0o440:"16LF1933", 0o442:"16LF1934", 0o443:"16LF1936", 0o444:"16LF1937",
			0o445:"16LF1938", 0o446:"16LF1939", 0o454:"16LF1946", 0o455:"16LF1947", 0o541:"16LF1902", 0o540:"16LF1903",
			0o544:"16LF1904", 0o543:"16LF1906", 0o542:"16LF1907",
			0x3020:"16F1454", 0x3024:"16LF1454", 0x3021:"16F1455", 0x3025:"16LF1455", 0x3023:"16F1459", 0x3027:"16LF1459",
			}

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
		signature = self.top.cmdReadBufferReg()[0:2 * idSize]
		devId = ((byte2int(signature[1]) << 8) | byte2int(signature[0])) >> self.nDeviceIdRevisionBits
		if(devId in self.deviceIdMapDict):
			print("device: {:s}".format(self.deviceIdMapDict.get(devId)))
		else:
			print("WARNING: device id {:o} not found in local dictionary".format(devId))
		return signature
			
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
