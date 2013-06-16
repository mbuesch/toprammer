"""
#    TOP2049 Open Source programming suite
#
#    Microchip common
#
#    Copyright (c) 2012 Pavel Stemberk <stemberk@gmail.com>
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

from libtoprammer.chip import *

class Chip_Microchip02_common(Chip):
	CMD_LOAD_CONFIGURATION    = 0x00
	CMD_LOAD_DATA_FOR_PGM     = 0x02
	CMD_READ_DATA_FROM_PGM    = 0x04
	CMD_INCREMENT_ADDRESS     = 0x06
	CMD_RESET_ADDRESS         = 0x16
	CMD_BEGIN_INTERNALLY_TIMED_PROGRAMMING     = 0x08
	CMD_BEGIN_EXTERNALLY_TIMED_PROGRAMMING     = 0x18
	CMD_END_EXTERNALLY_TIMED_PROGRAMMING       = 0x0A
	CMD_BULK_ERASE_PGM        = 0x09
	CMD_ROW_ERASE_PGM         = 0x11
	
	PROGCMD_SENDINSTR         = 1
	PROGCMD_SENDDATA          = 2
	PROGCMD_READDATA          = 3
	
	STAT_BUSY= 0x01
	STAT_SDIO = 0x02
    
	def __init__(self,
			chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
			signature,
			flashPageSize, flashPages,
			eepromPageSize, eepromPages,
			fuseBytes
			):
		Chip.__init__(self,
		chipPackage = chipPackage,
		chipPinVCC = chipPinVCC,
		chipPinsVPP = chipPinsVPP,
		chipPinGND = chipPinGND)
		self.signature = signature
		self.flashPageSize = flashPageSize    # Flash page size, in words
		self.flashPages = flashPages        # Nr of flash pages
		self.eepromPageSize = eepromPageSize    # EEPROM page size, in bytes
		self.eepromPages = eepromPages        # Nr of EEPROM pages
		self.fuseBytes = fuseBytes        # Nr of fuse bytes
		self.PC=0
		self.isInPmMode = False
		self.isInsideProgramMemoryArea = True
		#self.rowSize = rowSize
		#self.nLatches = nLatches
		#self.logicalFlashProgramMemorySize = logicalFlashProgramMemorySize
		#self.logicalFlashConfigurationMemorySize = logicalFlashConfigurationMemorySize


	def readSignature(self):
		self.progressMeterInit("Reading signature", 0)
		signature = self.__readSignature()
		self.progressMeterFinish()
		return signature
	
	def erase(self):
			self.__erase()
		
	def __erase(self, keepConfigWord=False, keepUserIDLocation=False):
		OSCCAL = 0xfff
		self.__enterPM()
		if(keepConfigWord):
			self.progressMeterInit("Reading ConfigWord for backup", 0)
			CW = self.__getConfigWord()
			self.progressMeterFinish()
		#erase User ID Location and backup osccal Tooo
		if(not keepUserIDLocation):
			self.__enterConfigArea()
			self.__setPC(self.userIDLocationAddr)
		self.progressMeterInit("Erasing chip", 0)
		self.__sendInstr(self.CMD_BULK_ERASE_PGM)
		self.top.hostDelay(0.01) #Tera
		self.progressMeterFinish()
		if(keepConfigWord):
			self.progressMeterInit("Write ConfigWord, value %x" % CW, 0)
			self.__writeConfigWord(CW)
			self.progressMeterFinish()
		self.__exitPM()


	def readProgmem(self):        
		nrWords = self.flashPages * self.flashPageSize
		image = ""
		self.__enterPM()
		self.progressMeterInit("Reading flash", nrWords)
		bufferedBytes = 0
		for word in range(0, nrWords):
			self.__incrementPC(1)
			self.__sendReadFlashInstr()
			#self.__busyWait()
			self.top.cmdDelay(0.00002) #20us wait - inconsistent data if skipped
			self.__readSDOBufferLow()
			bufferedBytes += 1
			self.__readSDOBufferHigh()
			bufferedBytes += 1
			if bufferedBytes == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(bufferedBytes)
				self.progressMeter(word)
				bufferedBytes = 0
		image += self.top.cmdReadBufferReg(bufferedBytes)
		self.progressMeterFinish()
		self.__exitPM()
		return image

	def writeProgmem(self, image):
		self.__enterPM()
		nrWords = self.flashPages * self.flashPageSize
		if len(image) > nrWords * 2 or len(image) % 2 != 0:
			self.throwError("Invalid flash image size %d (expected <=%d and word aligned)" %\
				(len(image), nrWords * 2))
		self.__enterPM()
		self.progressMeterInit("Writing flash", len(image) // 2)
		for wordAddr in range(0, len(image) // 2):
			self.progressMeter(wordAddr)
			#do not swap following two lines
			self.__incrementPC(1)
			self.__sendInstr(self.CMD_LOAD_DATA_FOR_PGM)
			WD = (byte2int(image[wordAddr * 2 + 1])<<8) | byte2int(image[wordAddr * 2 + 0])
			if(WD != 0xfff):
				self.__setSDI(WD)
				self.top.hostDelay(0.00002)
				self.__loadCommand(self.PROGCMD_SENDDATA)		
				self.top.hostDelay(0.000005)				
				self.__sendWriteFlashInstr()

		self.progressMeterFinish()
		self.__exitPM()

	def readFuse(self):
		self.__enterPM()
		fuses = []
		self.progressMeterInit("Reading fuses (configuration word)", 0)
		for CW in self.__getConfigWord(): 
			fuses.append(int2byte(CW & 0x00ff))
			fuses.append(int2byte((CW >> 8) & 0x00ff))
		self.progressMeterFinish()
		self.__exitPM()
		return b"".join(fuses)
	
	def readUserIdLocation(self):
		self.__enterPM()
		self.__enterConfigArea()
		self.__setPC(self.userIDLocationAddr)
		self.progressMeterInit("Reading User ID Location", 0)
		for i in range(0, self.userIDLocationSize):
			self.__sendReadFlashInstr()
			self.top.hostDelay(0.00002)
			self.__readSDOBufferLow()
			self.__readSDOBufferHigh()
			self.__incrementPC(1)
		self.__exitPM()
		self.progressMeterFinish()
		return self.top.cmdReadBufferReg()[0:2*self.userIDLocationSize]
	
	def writeUserIdLocation(self, image):
		if len(image) > self.userIDLocationSize * 2 or len(image) % 2 != 0:
			self.throwError("Invalid flash image size %d (expected <=%d and word aligned)" %\
				(len(image), self.userIDLocationSize * 2))
		self.__enterPM()
		self.__enterConfigArea()
		#self.__setPC(self.userIDLocationAddr)
		self.__setPC(0x2004)
		self.progressMeterInit("Writing User ID Location", (len(image) // 2) - 1)
		for word in range(0, (len(image) // 2)):
			self.progressMeter(word)
			#do not swap following two lines
			self.__sendInstr(self.CMD_LOAD_DATA_FOR_PGM)
			WD = (byte2int(image[word * 2 + 1])<<8) | byte2int(image[word * 2 + 0])
			self.__setSDI(WD)
			#self.top.hostDelay(0.00002)
			self.__loadCommand(self.PROGCMD_SENDDATA)
			self.__incrementPC(1)
		self.top.hostDelay(0.000005)				
		self.__sendWriteFlashInstr()
		self.progressMeterFinish()
		self.__exitPM()
		
	def __getConfigWordSize(self):
		return self.fuseBytes // 2

	def __getConfigWord(self):
		self.__enterPM()
		self.__enterConfigArea()
		self.__setPC(self.configWordAddr)
		retVal=[]
		for i in range(0,self.__getConfigWordSize()):
			self.__sendReadFlashInstr()
			self.top.cmdDelay(0.00002)
			self.__readSDOBufferLow()
			self.__readSDOBufferHigh()
			self.__incrementPC(1)
			retVal.append(self.top.cmdReadBufferReg16())

		return retVal

	def writeFuse(self, image):
		self.__enterPM()
		if len(image) != 2*self.__getConfigWordSize():
			self.throwError("Invalid Fuses image size %d (expected %d)" %\
				(len(image), 2*self.__getConfigWordSize()))
		self.progressMeterInit("Writing fuses", 0)
		#print "image1:%x,,%x,,%x" % (byte2int(image[0]),byte2int(image[1]),byte2int(image[1])<<8)
		CW=[]
		for tBytes in zip(image[::2],image[1::2]):
			CW.append((byte2int(tBytes[1])<<8) | byte2int(tBytes[0]))
		self.__writeConfigWord(CW)
		self.progressMeterFinish()
		self.__exitPM()
    
	def __writeConfigWord(self, listConfigWord16):
		#Externally timed writes are not supported
		#for Configuration and Calibration bits. Any
		#externally timed write to the Configuration
		#or Calibration Word will have no effect on
		#the targeted word.
		self.__enterPM()
		self.__enterConfigArea()
		self.__setPC(self.configWordAddr-1)
		print "PC:{:x}".format(self.PC)
		for configWord16 in listConfigWord16:
			self.__incrementPC(1)
			print "write CW {:x}".format(configWord16)
			self.__sendInstr(self.CMD_LOAD_DATA_FOR_PGM)
			self.__setSDI(configWord16)
			self.top.hostDelay(0.00002)
			self.__loadCommand(self.PROGCMD_SENDDATA)
			self.top.hostDelay(0.000005)
			self.__sendInstr(self.CMD_BEGIN_INTERNALLY_TIMED_PROGRAMMING)
			self.top.hostDelay(0.005)#TPINT
					

	def __readSignature(self):
		self.__enterPM()
		self.__enterConfigArea()
		self.__setPC(self.deviceIDAddr)
		idSize = 1
		for i in range(0, idSize):
			self.__sendReadFlashInstr()
			self.top.hostDelay(0.00002)
			self.__readSDOBufferLow()
			self.__readSDOBufferHigh()
			self.__incrementPC(1)
		self.__exitPM()
		return self.top.cmdReadBufferReg()[0:2*idSize]
		
	def __enterPM(self):
		if self.isInPmMode:
			self.__resetPC()
			return
		self.PC = 0
		"Enter HV programming mode. Vdd first entry mode"
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.__setPins(0,0)
		self.top.cmdSetVCCVoltage(self.voltageVDD)
		self.top.cmdSetVPPVoltage(self.voltageVPP)
		#self.top.cmdEnableZifPullups(True)
		self.applyGND(True)
		
		self.applyVCC(True)
		self.top.cmdDelay(0.000005)
		
		for i in range(0,2):
			self.applyVPP(True)
			self.top.cmdDelay(0.000005)
			self.applyVPP(False)
			self.top.cmdDelay(0.000031)
		self.applyVPP(True)
		#self.top.cmdEnableZifPullups(True)
		
		self.top.cmdDelay(0.000005) #least 5us is required to reach Vdd first entry PM
		self.isInPmMode=True

	def __checkSignature(self):
		signature = self.__readSignature()
		if signature != self.signature:
			msg = "Unexpected device signature. " +\
			 "Want %02X%02X%02X, but got %02X%02X%02X" % \
			(byte2int(self.signature[0]), byte2int(self.signature[1]),
			byte2int(self.signature[2]),
			byte2int(signature[0]), byte2int(signature[1]),
			byte2int(signature[2]))
		if self.top.getForceLevel() >= 1:
			self.printWarning(msg)
		else:
			self.throwError(msg)

	def __exitPM(self):
		"Exit HV programming mode. Vdd last exit mode"
		self.__setPins(0,0)
		self.applyVPP(False)
		self.applyGND(False)
		self.top.hostDelay(0.000005)
		self.applyVCC(False)
		self.isInPmMode=False

	def __sendReadFlashInstr(self):
		'''
		'''
		self.__sendInstr(self.CMD_READ_DATA_FROM_PGM)
		self.__loadCommand(self.PROGCMD_READDATA)

	def __sendWriteFlashInstr(self):
		'''
		'''
		self.__sendInstr(self.CMD_BEGIN_EXTERNALLY_TIMED_PROGRAMMING)
		self.top.hostDelay(0.001)#025) #Tprog
		self.__sendInstr(self.CMD_END_EXTERNALLY_TIMED_PROGRAMMING)
		self.top.hostDelay(0.0001) #Tdis

	def __sendInstr(self, SDI):
		'''
		see __loadCommand for availabla commands
		'''
		self.top.cmdFPGAWrite(0x13, SDI & 0xFF)
		self.__loadCommand(self.PROGCMD_SENDINSTR)
		# We do not poll the busy flag, because that would result
		# in a significant slowdown. We delay long enough for the
		# command to finish execution, instead.
		#self.top.hostDelay(0.001)
		self.top.hostDelay(0.000005)

	def __setSDI(self, sdi):
		'''
		set 14 bit sdi value
		'''
		self.top.cmdFPGAWrite(0x13, sdi & 0xFF)
		self.top.cmdFPGAWrite(0x14, (sdi>>8) & 0x3F)

	def __loadCommand(self, command):
		'''
		`define CMD_SENDINSTR   1
		`define CMD_SENDDATA    2
		`define CMD_READDATA    3
		'''
		self.top.cmdFPGAWrite(0x12, command & 0xFF)

	def __runCommandSync(self, command):
		self.__loadCommand(command)
		self.__busyWait()
        
	def __setPC(self, address):
		if(self.isInsideProgramMemoryArea):
			if(address >= self.logicalFlashProgramMemorySize):
				raise(TOPException('Cannot set PC to address {:x}'.format(address)))
			if(address < self.PC):
				self.__resetPC()
				self.__setPC(address)
		else:
			if(address < self.logicalFlashProgramMemorySize):
				raise(TOPException('Cannot set PC to address {:x}'.format(address)))
			if(address < self.PC):
				self.__resetPC()
				self.__enterConfigArea()
				self.__setPC(address)
		while(self.PC!=address):
			self.__incrementPC(1)

	def __incrementPC(self, count):
		for address in range(0, count):
			self.__sendInstr(self.CMD_INCREMENT_ADDRESS)
			self.PC += 1
			if(self.isInsideProgramMemoryArea):
				if (self.PC == self.logicalFlashProgramMemorySize):
					self.PC = 0
			else:
				if (self.PC == self.logicalFlashConfigurationMemorySize):
					self.PC = self.logicalFlashProgramMemorySize
	
	def __resetPC(self):
		self.__sendInstr(self.CMD_RESET_ADDRESS)
		self.PC = 0
		self.isInsideProgramMemoryArea = True

	def __enterConfigArea(self, wordLatched = 0):
		self.__sendInstr(self.CMD_LOAD_CONFIGURATION)
		self.__setSDI(wordLatched)
		#self.top.hostDelay(0.00002)
		self.__loadCommand(self.PROGCMD_SENDDATA)
		self.PC = self.logicalFlashProgramMemorySize
		self.isInsideProgramMemoryArea = False		

	def __setPins(self, ICSPCLK=0, SDIODRIVEN=0, SDIOVALUE=0):
		'''
		setPins
		'''
		data = 0
		if ICSPCLK:
			data |= 1
		if SDIODRIVEN:
			data |= 2
		if SDIOVALUE:
			data |= 4            
		self.top.cmdFPGAWrite(0x15, data)

	def __getStatusFlags(self):
		'''
		'''
		self.top.cmdFPGARead(0x12)
		stat = self.top.cmdReadBufferReg()
		return byte2int(stat[0])

	def __readSDOBufferHigh(self):
		self.top.cmdFPGARead(0x10)
	
	def __readSDOBufferLow(self):
		self.top.cmdFPGARead(0x13)        
	
	def __rawSDIOState(self):
		return bool(self.__getStatusFlags() & self.STAT_SDIO)

	def __busy(self):
		return bool(self.__getStatusFlags() & self.STAT_BUSY)

	def __busyWait(self):
		for i in range(0, 100):
			if not self.__busy():
				return
			self.top.hostDelay(0.01)
		self.throwError("Timeout in busywait.")

	def __waitHighSDIO(self):
		for i in range(0, 100):
			if self.__rawSDOState():
				return
			self.top.hostDelay(0.01)
		self.throwError("Timeout waiting for SDO.")
