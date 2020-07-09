"""
#    TOP2049 Open Source programming suite
#
#    Microchip8 common - basic file for 8bit PIC MCU
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
import math

class Chip_Microchip8_common(Chip):
	CMD_LOAD_DATA_FOR_PGM	 = 0x02
	CMD_LOAD_DATA_FOR_DM	 = 0x03
	CMD_READ_DATA_FROM_PGM	 = 0x04
	CMD_READ_DATA_FROM_DM	 = 0x05
	CMD_INCREMENT_ADDRESS	 = 0x06
	CMD_BULK_ERASE_PGM		 = 0x09
	CMD_BULK_ERASE_DM = 0x0B
	
	PCMDBIT_4BITINSTR 	 = 0
	PCMDBIT_SENDDATA	 = 1
	PCMDBIT_READDATA	 = 2
	
	STAT_BUSY = 0x01
	STAT_SDIO = 0x02

	# EEPROM access: default off, if exists override it
	hasEEPROM = False
	# Signature bytes access: default on, if doesn't exist, override it
	hasSigBytes = True

	# default delays - can be overridden
	delayTdly5 = 0.00000015
	delayTdis = 0.0001
	delayTprog = 0.001
	delayTdly = 0.000001
	delayTera = 0.01
	nLatches = 1

	@classmethod
	def getSupportFlags(cls):
		flags = super(Chip_Microchip8_common, cls).getSupportFlags()
		if not cls.hasEEPROM:
			flags &= ~(Chip.SUPPORT_EEPROMREAD |\
				   Chip.SUPPORT_EEPROMWRITE)
		if not cls.hasSigBytes:
			flags &= ~Chip.SUPPORT_SIGREAD
		return flags

	def __init__(self,
			chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
			signature,
			flashPageSize, flashPages,
			eepromPageSize, eepromPages,
			fuseBytes
			):
		Chip.__init__(self,
		chipPackage=chipPackage,
		chipPinVCC=chipPinVCC,
		chipPinsVPP=chipPinsVPP,
		chipPinGND=chipPinGND)
		self.signature = signature
		self.flashPageSize = flashPageSize  # Flash page size, in words
		self.flashPages = flashPages  # Nr of flash pages
		self.eepromPageSize = eepromPageSize  # EEPROM page size, in bytes
		self.eepromPages = eepromPages  # Nr of EEPROM pages
		self.fuseBytes = fuseBytes  # Nr of fuse bytes
		self.PC = 0
		self.isInPmMode = False

	def erase(self):
		if(hasattr(self, 'osccalAddr')):
			self.__erase(keepOSCCAL=True)
		else:
			self.__erase(keepOSCCAL=False)
		
	def __erase(self, keepConfigWord=False, keepUserIDLocation=False, keepOSCCAL=False, keepEEPROM=False):
		OSCCAL = 0xfff
		self.exitPM()
		self.enterPM()
		if(keepOSCCAL):
			self.progressMeterInit("Reading OSCCAL)", 0)
			self.setPC(self.osccalAddr)
			self.sendReadFlashInstr()
			self.top.cmdDelay(self.delayTdly)
			self.readSDOBufferLow()
			self.readSDOBufferHigh()
			OSCCAL = self.top.cmdReadBufferReg16()
			self.progressMeterFinish()
			if(hasattr(self, 'osccalBackupAddr') and OSCCAL == 0xfff):
				self.progressMeterInit("OSCCAL value lost, restoring from backup location ...", 0)
				print("OSCCAL value lost, restoring from backup location ...")
				self.setPC(self.osccalBackupAddr - self.osccalAddr)
				self.sendReadFlashInstr()
				self.top.cmdDelay(self.delayTdly)
				self.readSDOBufferLow()
				self.readSDOBufferHigh()
				OSCCAL = self.top.cmdReadBufferReg16()
				self.progressMeterFinish()
				# print ("osccal: %x\n" % OSCCAL)
		if(keepConfigWord):
			self.progressMeterInit("Reading ConfigWord for backup", 0)
			CW = self.getConfigWord()
			self.progressMeterFinish()
		# erase User ID Location and backup osccal Tooo
		# erase User ID Location and backup osccal Tooo
		if(not keepUserIDLocation):
			self.enterConfigArea()
			self.setPC(self.userIDLocationAddr)
		self.progressMeterInit("Erasing chip", 0)
		self.bulkErasePGM()
		self.progressMeterFinish()
		#OSCCAL=0x3454
		#OSCCAL=0x0C10
		if(keepOSCCAL and OSCCAL != 0xfff):
			self.exitPM()
			self.enterPM()
			self.progressMeterInit("Writing osccal,  value %x" % OSCCAL, 0)
			print("Writing osccal,  value %x" % OSCCAL)
			self.setPC(self.osccalAddr)
			self.send6bitWriteInstruction(self.CMD_LOAD_DATA_FOR_PGM, OSCCAL)
			self.top.cmdDelay(self.delayTdly)
			self.sendWriteFlashInstr()
			self.progressMeterFinish()
		if(keepConfigWord):
			self.progressMeterInit("Writing ConfigWord, value %x" % CW, 0)
			self.writeConfigWord(CW)
			self.progressMeterFinish()
		if((not keepEEPROM) and self.hasEEPROM):
			self.progressMeterInit("Erasing EEPROM", 0)
			self.bulkEraseDM()
			self.progressMeterFinish()
		self.exitPM()

	def bulkErasePGM(self):
		self.sendCommand(0, 0, 0, self.CMD_BULK_ERASE_PGM)
		self.top.cmdDelay(self.delayTera)  # Tera
		
	def bulkEraseDM(self):
		self.sendCommand(0, 0, 0, self.CMD_BULK_ERASE_DM)
		self.top.cmdDelay(self.delayTera)  # Tera
		
	def readProgmem(self):	
		nrWords = self.flashPages * self.flashPageSize
		image = b""
		self.enterPM()
		self.setPC(0)
		self.progressMeterInit("Reading flash", nrWords)
		bufferedBytes = 0
		for word in range(0, nrWords):
			self.sendReadFlashInstr()
			# self.top.cmdDelay(0.00002) #20us wait - inconsistent data if skipped
			self.top.cmdDelay(self.delayTdly)
			
			self.readSDOBufferLow()
			bufferedBytes += 1
			self.readSDOBufferHigh()
			bufferedBytes += 1
			if bufferedBytes == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(bufferedBytes)
				self.progressMeter(word)
				bufferedBytes = 0
			self.incrementPC(1)
		image += self.top.cmdReadBufferReg(bufferedBytes)
		self.progressMeterFinish()
		# self.exitPM()
		return image
	
	def readEEPROM(self):	
		nrWords = self.eepromPages * self.eepromPageSize
		image = b""
		self.enterPM()
		self.progressMeterInit("Reading eeprom", nrWords)
		bufferedBytes = 0
		for word in range(0, nrWords):
			self.sendReadEEPROMInstr()
			self.top.cmdDelay(self.delayTdly)  # 20us wait - inconsistent data if skipped
			self.readSDOBufferLow()
			bufferedBytes += 1
			if bufferedBytes == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(bufferedBytes)
				self.progressMeter(word)
				bufferedBytes = 0
			self.incrementPC(1)
		image += self.top.cmdReadBufferReg(bufferedBytes)
		self.progressMeterFinish()
		# self.exitPM()
		return image

	def writeEEPROM(self, image):	
		nrWords = self.eepromPages * self.eepromPageSize
		if len(image) > nrWords:
			self.throwError("Invalid flash image size %d (expected <=%d)" % len(image))
		self.enterPM()
		self.progressMeterInit("Writing eeprom", nrWords)
		bufferedBytes = 0
		for addr in range(0, len(image)):
			self.progressMeter(addr)
			byte = byte2int(image[addr])
			if byte != 0xff:
				self.send6bitWriteInstruction(self.CMD_LOAD_DATA_FOR_DM, byte)
				self.top.cmdDelay(self.delayTdly)
				self.sendWriteFlashInstrDM()				
			self.incrementPC(1)
		self.progressMeterFinish()
		# self.exitPM()

	def writeProgmem(self, image):
		nrWords = self.flashPages * self.flashPageSize
		if len(image) > nrWords * 2 or len(image) % 2 != 0:
			self.throwError("Invalid flash image size %d (expected <=%d and word aligned)" % \
				(len(image), nrWords * 2))
		self.progressMeterInit("Writing flash", len(image) // 2)
		self.enterPM()
		self.setPC(0)
		latCnt=1;
		writeCurrentLatches=False
		for wordAddr in range(0, len(image) // 2):
			self.progressMeter(wordAddr)
			# do not swap following two lines
			WD = (byte2int(image[wordAddr * 2 + 1]) << 8) | byte2int(image[wordAddr * 2 + 0])
			if(WD != (byte2int(self.defaultWord[1]) << 8) + byte2int(self.defaultWord[0])):
				self.send6bitWriteInstruction(self.CMD_LOAD_DATA_FOR_PGM, WD)
				self.top.cmdDelay(self.delayTdly)				
				writeCurrentLatches=True
			if(latCnt == self.nLatches):
				if(writeCurrentLatches):
					self.sendWriteFlashInstr()
				latCnt=0
				writeCurrentLatches=False
			latCnt+=1
			self.incrementPC(1)
		if(latCnt>1):
			self.sendWriteFlashInstr()
		self.progressMeterFinish()
		# self.exitPM()

	def readFuse(self):
		self.enterPM()
		fuses = []
		self.progressMeterInit("Reading fuses (configuration word)", 0)
		for CW in self.getConfigWord(): 
			fuses.append(int2byte(CW & 0x00ff))
			fuses.append(int2byte((CW >> 8) & 0x00ff))
		self.progressMeterFinish()
		return b"".join(fuses)
	
	def readUserIdLocation(self):
		self.enterPM()
		self.enterConfigArea()
		self.setPC(self.userIDLocationAddr)
		self.progressMeterInit("Reading User ID Location", 0)
		for i in range(0, self.userIDLocationSize):
			self.sendReadFlashInstr()
			self.top.hostDelay(self.delayTdly)
			self.readSDOBufferLow()
			self.readSDOBufferHigh()
			self.incrementPC(1)
		# self.exitPM()
		self.progressMeterFinish()
		return self.top.cmdReadBufferReg()[0:2 * self.userIDLocationSize]
	
	def writeUserIdLocation(self, image):
		if len(image) > self.userIDLocationSize * 2 or len(image) % 2 != 0:
			self.throwError("Invalid flash image size %d (expected <=%d and word aligned)" % \
				(len(image), self.userIDLocationSize * 2))
		self.enterPM()
		self.enterConfigArea()
		self.setPC(self.userIDLocationAddr)
		self.progressMeterInit("Writing User ID Location", (len(image) // 2) - 1)
		for word in range(0, (len(image) // 2)):
			self.progressMeter(word)
			# do not swap following two lines
			WD = (byte2int(image[word * 2 + 1]) << 8) | byte2int(image[word * 2 + 0])
			if(WD != (byte2int(self.defaultWord[1]) << 8) + byte2int(self.defaultWord[0])):
				self.send6bitWriteInstruction(self.CMD_LOAD_DATA_FOR_PGM, WD)
				self.sendWriteFlashInstr()
			self.incrementPC(1)
		self.top.hostDelay(self.delayTdly)
		self.sendWriteFlashInstr()
		self.progressMeterFinish()
		# self.exitPM()
		
	def getConfigWordSize(self):
		return self.fuseBytes // 2

	def getConfigWord(self):
		self.enterPM()
		self.enterConfigArea()
		self.setPC(self.configWordAddr)
		retVal = []
		for i in range(0, self.getConfigWordSize()):
			self.sendReadFlashInstr()
			self.top.cmdDelay(self.delayTdly)
			self.readSDOBufferLow()
			self.readSDOBufferHigh()
			self.incrementPC(1)
			retVal.append(self.top.cmdReadBufferReg16())

		return retVal

	def writeFuse(self, image):
		if len(image) != 2 * self.getConfigWordSize():
			self.throwError("Invalid Fuses image size %d (expected %d)" % \
				(len(image), 2 * self.getConfigWordSize()))
		self.progressMeterInit("Writing fuses", 0)
		# print "image1:%x,,%x,,%x" % (byte2int(image[0]),byte2int(image[1]),byte2int(image[1])<<8)
		CW = []
		for tBytes in zip(image[::2], image[1::2]):
			CW.append((byte2int(tBytes[1]) << 8) | byte2int(tBytes[0]))
		self.writeConfigWord(CW)
		self.progressMeterFinish()
    
	def writeConfigWord(self, listConfigWord16):
		# Externally timed writes are not supported
		# for Configuration and Calibration bits. Any
		# externally timed write to the Configuration
		# or Calibration Word will have no effect on
		# the targeted word.
		self.enterPM()
		self.enterConfigArea()
		self.setPC(self.configWordAddr)
		for configWord16 in listConfigWord16:
			# print "write CW {:x}".format(configWord16)
			self.send6bitWriteInstruction(self.CMD_LOAD_DATA_FOR_PGM, configWord16)
			self.top.cmdDelay(self.delayTdly)
			self.sendWriteFlashInstrCW()
			self.incrementPC(1)
		self.top.flushCommands()
					

		
	def enterPM(self):
		if self.isInPmMode and self.isInsideProgramMemoryArea:
			self.resetPC()
			return
		self.PC = self.initPcValue
		self.isInsideProgramMemoryArea = True
		"Enter HV programming mode. Vdd first entry mode"
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.setPins(0, 0)
		self.top.cmdSetVCCVoltage(self.voltageVDD)
		self.top.cmdSetVPPVoltage(self.voltageVPP)
		# self.top.cmdEnableZifPullups(True)
		self.applyGND(True)
		
		self.applyVPP(True)
		self.top.cmdDelay(0.000250)
		
		
		self.applyVCC(True)
		# self.top.cmdEnableZifPullups(True)
		
		# self.top.cmdDelay(0.000005) #least 5us is required to reach Vdd first entry PM
		self.setTopProgrammerDelays()
		self.isInPmMode = True

	def checkSignature(self):
		signature = self.readSignature()
		if signature != self.signature:
			msg = "Unexpected device signature. " + \
			 "Want %02X%02X%02X, but got %02X%02X%02X" % \
			(byte2int(self.signature[0]), byte2int(self.signature[1]),
			byte2int(self.signature[2]),
			byte2int(signature[0]), byte2int(signature[1]),
			byte2int(signature[2]))
		if self.top.getForceLevel() >= 1:
			self.printWarning(msg)
		else:
			self.throwError(msg)

	def exitPM(self):
		"Exit HV programming mode. Vdd last exit mode"
		self.top.flushCommands()
		self.setPins(0, 0)
		self.applyVPP(False)
		self.applyGND(False)
		self.top.hostDelay(self.delayTdly)
		self.applyVCC(False)
		self.isInPmMode = False

	def sendReadFlashInstr(self):
		'''
		'''
		self.sendCommand(0, 0, 1, self.CMD_READ_DATA_FROM_PGM)

	def sendWriteFlashInstr(self):
		'''
		to be overriden
		'''
		pass
		
	def sendReadEEPROMInstr(self):
		'''
		'''
		self.sendCommand(0, 0, 1, self.CMD_READ_DATA_FROM_DM)

	def send6bitReadInstruction(self, pInstruction):
		def incBbAndCheckFillImage():
			self.BufferedBytes += 1
			if self.BufferedBytes == self.top.getBufferRegSize():
				self.flushBufferToImage()
		# self.sendCommand(1,0,1,pInstruction)
		self.sendCommand(0, 0, 1, pInstruction)
		# self.busyWait()
		self.readSDOBufferHigh()
		incBbAndCheckFillImage()
		
	def send6bitWriteInstruction(self, pInstruction, pDataPayload):
		# self.busyWait()
		self.setSDI(pDataPayload)
		# print("sending {:x}\n".format(pDataPayload))
		self.sendCommand(0, 1, 0, pInstruction)
		self.top.flushCommands()

	def setSDI(self, sdi):
		'''
		set 14 bit sdi value
		'''
		self.top.cmdFPGAWrite(0x13, sdi & 0xFF)
		self.top.cmdFPGAWrite(0x14, (sdi >> 8) & 0x3F)

	def sendCommand(self, bit4bitInstr=0, bitSendData=0, bitReadData=0, cmd4bit=0):
		'''
		`define CMDBIT_4BITINSTR 0
		`define CMDBIT_SENDDATA	1
		`define CMDBIT_READDATA	2
		'''
		command = (cmd4bit & 0x1F) << 3
		if bit4bitInstr:
			command |= 2 ** self.PCMDBIT_4BITINSTR
		if bitSendData:
			command |= 2 ** self.PCMDBIT_SENDDATA
		if bitReadData:
			command |= 2 ** self.PCMDBIT_READDATA
		# print("cmd sending {:x}\n".format(command))
		self.top.cmdFPGAWrite(0x12, command)
		
	def setTopProgrammerDelays(self):
		#print("tdel5:{:d}".format(int(math.ceil(self.delayTdly5 / 42e-9))))
		#print("tdly:{:d}".format(int(math.ceil(self.delayTdly / 42e-9))))
		self.top.cmdFPGAWrite(0x10, int(math.ceil(self.delayTdly5 / 42e-9)))
		self.top.cmdFPGAWrite(0x11, int(math.ceil(self.delayTdly / 42e-9)))

# 	def runCommandSync(self, command):
# 		self.loadCommand(command)
# 		self.busyWait()
	def resetPC(self):
		'''can be overriden'''
		self.setPC(self.initPcValue)
			
	def setPC(self, address):
		'''to be overriden'''
		pass

	def incrementPC(self, count):
		'''to be overriden'''
		pass
	
	def enterConfigArea(self, wordLatched=0):
		'''to be overriden'''
		pass

	def setPins(self, ICSPCLK=0, SDIOVALUE=0, SDIODRIVEN=1):
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

	def getStatusFlags(self):
		'''
		'''
		self.top.cmdFPGARead(0x12)
		stat = self.top.cmdReadBufferReg()
		return byte2int(stat[0])

	def readSDOBufferHigh(self):
		self.top.cmdFPGARead(0x10)
	
	def readSDOBufferLow(self):
		self.top.cmdFPGARead(0x13)	
	
	def rawSDIOState(self):
		return bool(self.getStatusFlags() & self.STAT_SDIO)

	def busy(self):
		return bool(self.getStatusFlags() & self.STAT_BUSY)

# 	def busyWait(self):
# 		for i in range(0, 100):
# 			if not self.busy():
# 				return
# 			self.top.hostDelay(0.01)
# 		self.throwError("Timeout in busywait.")

# 	def waitHighSDIO(self):
# 		for i in range(0, 100):
# 			if self.rawSDOState():
# 				return
# 			self.top.hostDelay(0.01)
# 		self.throwError("Timeout waiting for SDO.")
