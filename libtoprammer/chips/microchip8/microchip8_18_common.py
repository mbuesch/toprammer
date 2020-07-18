"""
#    TOP2049 Open Source programming suite
#
#    Microchip8_18_common - basic file for 8bit PIC18 MCU
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

from libtoprammer.chip import *

class Chip_Microchip8_18_common(Chip):
	
	STAT_BUSY = 0x01
	STAT_SDIO = 0x02

	
	PCMDBIT_4BITINSTR 	 = 0
	PCMDBIT_SENDDATA		 = 1
	PCMDBIT_READDATA		 = 2	
	PCMDBIT_KEEPCLKHIGH	 = 7	
	
	CMD_CORE_INSTRUCTION	 = 0x0
	CMD_SHIFT_OUT_TABLAT	 = 0x2
	CMD_TR					 = 0x8
	CMD_TRI					 = 0x9
	CMD_TRD					 = 0xA
	CMD_ITR					 = 0xB
	CMD_TW					 = 0xC
	CMD_TWII				 = 0xD
	CMD_TWDD				 = 0xE
	CMD_TW_START_PROG		 = 0xF

	# EEPROM access: default on, if does not exist override it
	hasEEPROM = True

	# default delays - can be overridden
	delayP2A = 400e-9  # Serial clock low time 
	delayP5 = 2.2e-6  # Delay between 4-bit command and command operand
	delayP5A = 2.2e-6  # Delay between 4-bit command operand and next 4-bit command 
	delayP6 = 2.2e-6  # Delay between last SCK fall of command byte to first SCK rise of read data word
	delayP9 = 1e-3  # SCK High time (minimum programming time)
	delayP10 = 30e-6  # SCK Low time after programming (high-voltage discharge time)
	delayP11 = 0.01  # Delay to allow self-timed data write or bulk erase to occur
	delayP12 = 0.000002  # Input data hold time from nMCLR/Vpp rise
	delayP13 = 0.0000001  # Vdd rise setup time to nMCLR/Vpp rise
	delayP14 = 0.00000001  # Data out Valid from SCK rise
	delayP15 = 0.000002  # PGM rise setup time to nMCLR/Vpp rise
  	
	userIDLocationSize		 = 8
	userIDLocationAddr  	 = 0x200000

	deviceIDAddr 			 = 0x3FFFFE
	configWordAddr			 = 0x300000
	deviceIDLength 			 = 2
	voltageVDD				 = 5
	voltageVPP				 = 12

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
		self.isInPmMode = False
		self.BufferedBytes = 0
		self.Image = b""

	def getIHexInterpreter(self):
		inter = IHexInterpreter()
		inter.progmemRanges = [ AddressRange(0, self.flashPageSize) ]
		inter.fuseRanges = [ AddressRange(self.configWordAddr,
						  self.configWordAddr + self.fuseBytes) ]
		inter.uilRanges = [ AddressRange(self.userIDLocationAddr,
						 self.userIDLocationAddr + self.userIDLocationSize) ]
		return inter

	def enterPM(self, force=False):
		if self.isInPmMode and not force:
			return
		"Enter HV programming mode. Vdd first entry mode"
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.setPins(0, 0)
		self.top.cmdSetVCCVoltage(self.voltageVDD)
		self.top.cmdSetVPPVoltage(self.voltageVPP)
		self.applyGND(True)
		self.applyVCC(True)
		self.top.hostDelay(10 * self.delayP13)
		self.applyVPP(True)
		self.top.hostDelay(102 * self.delayP12)
		self.setTopProgrammerDelays()
		self.isInPmMode = True
	
	def readUserIdLocation(self):
		return self.readSequentialBlock(self.userIDLocationAddr, self.userIDLocationSize, "Reading User ID Locations")
	
	def readFuse(self):
		return self.readSequentialBlock(self.configWordAddr, self.fuseBytes, "Reading Config Words")
	
	def readSignature(self):
		return self.readSequentialBlock(self.deviceIDAddr, self.deviceIDLength, "Reading Signature")

	def readProgmem(self):	
		nrBytes = self.flashPages * self.flashPageSize
		return self.readSequentialBlock(0, nrBytes, "Reading flash")
	
	def readSequentialBlock(self, startAddr, nBytes, infoText):	
		self.enterPM()
		self.progressMeterInit(infoText, nBytes)
		self.BufferedBytes = 0
		self.Image = b""
		self.executeCode(self.getCodeAddrToTBLPTR(startAddr))
		for byteAddr in range(0, nBytes):
			self.send4bitReadInstruction(self.CMD_TRI)
			self.progressMeter(byteAddr)
		self.progressMeterFinish()
		self.flushBufferToImage()
		return self.Image
	
	def writeSequentialBlock(self, startAddr, image, size, infoText):
		if len(image) > size:
			self.throwError("Invalid flash image size %d (expected <=%d)" % \
				(len(image), self.userIDLocationSize))
		self.enterPM()
		self.executeCode((0x8EA6, 0x9CA6))
		self.progressMeterInit(infoText, len(image) // 8)
		for blockAddr in range(0, len(image), self.writeBufferSize):
			#print("addr:{:x}".format(startAddr+blockAddr))
			self.executeCode(self.getCodeAddrToTBLPTR(startAddr+blockAddr))
			#for code in self.getCodeAddrToTBLPTR(startAddr+blockAddr):
			#	print("({:x}, ".format(code))
			print(")\n")
			self.writeNbytes(image[blockAddr:], self.writeBufferSize)
			#self.executeCode((0x0, 0x0))
			self.progressMeter(blockAddr)
		self.progressMeterFinish()
			
	def readEEPROM(self):      
		nrBytes = self.eepromPages * self.eepromPageSize
		self.enterPM()
		self.progressMeterInit("Reading EEPROM", nrBytes)
		self.BufferedBytes = 0
		self.Image = b""
		self.executeCode((0x9EA6, 0x9CA6))
		for byteAddr in range(0, nrBytes):
			# print("set addr to {:x}\n".format(byteAddr))
			self.setEEPROMAddr(byteAddr)
			self.executeCode((0x80A6, 0x50A8, 0x6EF5))
			self.send4bitReadInstruction(self.CMD_SHIFT_OUT_TABLAT)
			self.progressMeter(byteAddr)
		self.progressMeterFinish()
		self.flushBufferToImage()
		return self.Image
	
	def writeEEPROM(self, image):	
		nrBytes = self.eepromPages * self.eepromPageSize
		if len(image) > nrBytes:
			self.throwError("Invalid flash image size {:d} (expected <={:d})".format(len(image), nrBytes))
		self.enterPM()
		self.progressMeterInit("Writing eeprom", len(image))
		self.executeCode((0x9EA6, 0x9CA6))
		for addr in range(0, len(image)):
			self.progressMeter(addr)
			#print("writing {:x} value to addr {:x}\n".format(byte2int(image[addr]), addr))
			self.setEEPROMAddr(addr)
			self.executeCode((0x0E00 | (byte2int(image[addr]) & 0xFF), 0x6EA8))
			self.executeCode((0x84A6, 0x0E55, 0x6EA7, 0x0EAA, 0x6EA7))
			self.executeCode((0x82A6, 0x0, 0x0))
			self.top.hostDelay(self.delayP11 + self.delayP10)
			self.executeCode((0x94A6,))
		self.progressMeterFinish()

	def writeNbytes(self, image, N):
		if N % 2:
			self.throwError("N should be even, not %d" % N)	
		isEmpty = True
		#N = (pN, len(image))[len(image) < pN]
		for idx in range(0, N):
			if idx == len(image):
				image += b'\xFF'
			elif byte2int(image[idx]) != 0xFF:
				isEmpty = False
		if(not isEmpty):
			for wordAddr in range(0, N-2, 2):
				self.send4bitWriteInstruction(self.CMD_TWII, byte2int(image[wordAddr]) | (byte2int(image[wordAddr + 1]) << 8))
			self.send4bitWriteInstruction(self.CMD_TW_START_PROG, byte2int(image[N-2]) | (byte2int(image[N-1]) << 8))
			self.top.cmdFPGAWrite(0x12, 0x81)
			self.top.hostDelay(self.delayP9)
			self.setPins(0)
			self.top.cmdDelay(self.delayP10)
			for i in range(0,4):
				self.sendCommand(1)

	def writeUserIdLocation(self, image):
		self.writeSequentialBlock(self.userIDLocationAddr, image, self.userIDLocationSize, "Writing User ID Locations")

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

	def writeProgmem(self, image):
		nrBytes = self.flashPages * self.flashPageSize
		if len(image) > nrBytes:
			self.throwError("Invalid flash image size %d (expected <=%d)" % \
				(len(image), nrBytes))
		self.writeSequentialBlock(0, image, nrBytes, "Writing flash")

	def writeFuse(self, image):
		self.enterPM()
		if len(image) > self.fuseBytes:
			self.throwError("Invalid Fuses image size %d (expected less than %d)" % \
				(len(image), self.fuseBytes))		
		self.executeCode((0x8EA6, 0x8CA6, 0xEF00, 0xF800))
		for fuseAddr in range(0,len(image)):
			self.executeCode(self.getCodeAddrToTBLPTR(self.configWordAddr+fuseAddr))
			if(fuseAddr & 0x01):
				byte =  byte2int(image[fuseAddr]) << 8
			else:
				byte =  byte2int(image[fuseAddr])
			self.send4bitWriteInstruction(self.CMD_TW_START_PROG, byte)
			self.top.cmdFPGAWrite(0x12, 0x81)
			#self.setPins(1)
			self.top.hostDelay(self.delayP9)
			self.setPins(0)
			self.top.cmdDelay(self.delayP10)
			for i in range(0,4):
				self.sendCommand(1)
			#self.executeCode((0x2AF6,))
		self.writeSequentialBlock(self.configWordAddr, image, self.fuseBytes, "Writing fuses")
		self.progressMeterInit("Writing fuses", 0)
						
	def exitPM(self):
		"Exit programming mode. Vdd last exit mode"
		self.top.flushCommands()
		self.setPins(0, 0)
		self.applyVPP(False)
		self.applyVCC(False)
		self.applyGND(False)
		self.isInPmMode = False

# ready for 18F below
	def send4bitReadInstruction(self, pInstruction):
		def incBbAndCheckFillImage():
			self.BufferedBytes += 1
			if self.BufferedBytes == self.top.getBufferRegSize():
				self.flushBufferToImage()
		# self.sendCommand(1,0,1,pInstruction)
		self.sendCommand(1, 0, 1, pInstruction)
		# self.busyWait()
		self.readSDOBufferHigh()
		incBbAndCheckFillImage()
		
	def send4bitWriteInstruction(self, pInstruction, pDataPayload):
		# self.busyWait()
		self.setSDI(pDataPayload)
		#print("sending {:x}\n".format(pDataPayload))
		self.sendCommand(1, 1, 0, pInstruction)
		self.top.flushCommands()
		
	def sendCommand(self, bit4bitInstr=1, bitSendData=0, bitReadData=0, cmd4bit=0, bitKeepClkHigh=0):
		'''
		`define CMDBIT_4BITINSTR 0
		`define CMDBIT_SENDDATA	1
		`define CMDBIT_READDATA	2
		`define CMDBIT_KEEPCLKHIGH 7
		'''
		command = (cmd4bit & 0x0F) << 3
		if bit4bitInstr:
			command |= 2 ** self.PCMDBIT_4BITINSTR
		if bitSendData:
			command |= 2 ** self.PCMDBIT_SENDDATA
		if bitReadData:
			command |= 2 ** self.PCMDBIT_READDATA
		if bitKeepClkHigh:
			command |= 2 ** self.PCMDBIT_KEEPCLKHIGH
		# print("cmd sending {:x}\n".format(command))
		self.top.cmdFPGAWrite(0x12, command)
		if(bitSendData or bitReadData):
			self.top.cmdDelay(2 * 20 * 2 * self.delayP2A)
		else:
			self.top.cmdDelay(2 * 4 * 2 * self.delayP2A)
		
	def setTopProgrammerDelays(self):
		#print("tdel5:{:d}".format(int(math.ceil(self.delayP2A / 42e-9))))
		#print("tdly:{:d}".format(int(math.ceil(self.delayP5 / 42e-9))))
		self.top.cmdFPGAWrite(0x10, int(math.ceil(self.delayP2A / 42e-9)))
		self.top.cmdFPGAWrite(0x11, int(math.ceil(self.delayP5 / 42e-9)))		

	def setSDI8(self, sdi):
		self.top.cmdFPGAWrite(0x16, sdi & 0xFF)
			
	def setSDI(self, sdi):
		'''
		16 -set 16 bit sdi value
		'''
		for addr in (0x16, 0x17):
			self.top.cmdFPGAWrite(addr, sdi & 0xFF)
			sdi = sdi >> 8
		
	def flushBufferToImage(self):
		# print ("storing {:d} bytes to image".format(self.BufferedBytes))
		if self.BufferedBytes > 0:
			self.Image += self.top.cmdReadBufferReg(self.BufferedBytes)
			self.BufferedBytes = 0
	
	def sendInstruction(self, instr):
		self.setSDI(instr)
		self.sendCommand(1, 1)  # send 4 times positive edge
		# self.top.flushCommands()
		
	def executeCode(self, code):
		for instr in code:
			self.sendInstruction(instr)

	def setPins(self, ICSPCLK=0, SDIOVALUE=0, SDIODRIVEN=1):
		'''
		16 - setPins
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
		[0] - BUSY
		[1] - SDO
		'''
		self.flushBufferToImage()
		self.top.cmdFPGARead(0x12)
		stat = self.top.cmdReadBufferReg()
		return byte2int(stat[0])

	def readSDOBufferHigh(self):
		self.top.cmdFPGARead(0x14)
	
	def readSDOBufferLow(self):
		self.top.cmdFPGARead(0x15)	
	
	def rawSDIOState(self):
		return bool(self.getStatusFlags() & self.STAT_SDIO)
	
	def isBusy(self):
		return bool(self.getStatusFlags() & self.STAT_BUSY)

	def busyWait(self):
		for i in range(0, 100):
			if not self.isBusy():
				return
			self.top.hostDelay(0.000001)
		self.throwError("Timeout in busywait.")

	def getCodeAddrToTBLPTR(self, addr):
		ub = (addr >> 16) & 0xFF
		hb = (addr >> 8) & 0xFF
		lb = addr & 0xFF
		return ((0x0E00 | ub), 0x6EF8, (0x0E00 | hb), 0x6EF7, (0x0E00 | lb), 0x6EF6)
