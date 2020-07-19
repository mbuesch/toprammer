"""
#    TOP2049 Open Source programming suite
#
#    Microchip8 common - basic file for 16bit PIC MCU
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

class Chip_Microchip16_common(Chip):
	STAT_BUSY = 0x01
	STAT_SDIO = 0x02

	PROGCMD_SENDSIXINSTR	 = 0
	PROGCMD_SENDREGOUTINSTR	 = 1
	PROGCMD_ENTERPM 	 = 2
	PROGCMD_SEND9SIXINSTR	 = 3

	codeExitResetVector = (0x000000, 0x040200, 0x000000)
	codeExitResetVectorSimple = (0x040200, 0x000000)
	codeInitializeW7toVISI = (0x207847, 0x000000)
	codeResetDeviceInternalPC = (0x040200, 0x000000)

	# EEPROM access: default on, if does not exist override it
	hasEEPROM = True
	eepromStartAddress = 0x7FFE00

	# default delays - can be overridden
	delayTdis = 0.0001
	delayTprog = 0.001
	delayCommandDataREGOUT = 0.0000005
	delayTera = 0.01
	# delayP3 = 0.000000015 # Input Data Hold Time from PGECx rise
	delayP3 = 0.00000006  # this is hard-tuned value !
	delayP4 = 0.000000040  # Delay between 4-Bit Command Operand and Command Operand
	delayP4A = 0.000000040  # Delay between 4-Bit Command Operand and the Next 4-bit command
	delayP5 = 0.000000020  # Delay between Last PGCx fall of Command Byte and First PGC rise by Programming Executive
	delayP6 = 0.000000100  # Vdd rise setup time to nMCLR rise
	delayP7 = 0.025  # Input data Hold Time from nMCLR rise, Vpp fall
	delayP11 = 0.0025  # chip Erase Time
	delayP13 = 0.00125  # row programming time
	delayP16 = 0  # delay between last PGCx fall and nMCLR fall
	delayP17 = 0.000000100  # nMCLR fall to Vdd fall
	delayP18 = 0.001  # delay between first nMCLR fall and first PGCx rise
	delayP19 = 0.001  # delay between last PGC fall for key sequence on PGDx and second nMCLR rise

	deviceIDAddr = 0xFF0000
	deviceIDLength = 1

	deviceIdMapDict = {
			0x0d00:"24f04ka201", 0x0d02:"24f04ka200", 0x4b14:"24f16kl402", 0x4b1e:"24f16kl401", 0x4b04:"24f08kl402", 0x4b0e:"24f08kl401",
			0x4b00:"24f08kl302", 0x4b0a:"24f08kl301", 0x4b06:"24f08kl201", 0x4b05:"24f08kl200", 0x4b02:"24f04kl101", 0x4b01:"24f04kl100"
	}

	def getIHexInterpreter(self):
		inter = IHexInterpreter()
		inter.progmemRanges = [ AddressRange(0, 2 * self.flashPageSize) ]
		inter.fuseRanges = [ AddressRange(2 * self.configWordAddr,
						  2 * self.configWordAddr + 1) ]
		return inter

	@classmethod
	def getSupportFlags(cls):
		flags = super(Chip_Microchip16_common, cls).getSupportFlags()
		if not cls.hasEEPROM:
			flags &= ~(Chip.SUPPORT_EEPROMREAD | \
				   Chip.SUPPORT_EEPROMWRITE)
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
		self.isInPmMode = False
		self.BufferedBytes = 0
		self.Image = b""

	def enterPM(self, lowVoltageIcspEntry=True):
		if self.isInPmMode:
			return
		"Enter HV programming mode. Vdd first entry mode"
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.setPins(0, 0)
		self.top.cmdSetVCCVoltage(self.voltageVDD)
		self.top.cmdSetVPPVoltage((self.voltageVPP, self.voltageVDD)[lowVoltageIcspEntry])
		self.applyGND(True)
		self.applyVCC(True)
		self.top.hostDelay(self.delayP6)
		self.applyVPP(True)
		self.setTopProgrammerDelays();
		if lowVoltageIcspEntry:
			self.top.hostDelay(self.delayP6)
			self.applyVPP(False)
		self.top.hostDelay(self.delayP18)
		self.sendCommand(self.PROGCMD_ENTERPM)
		if lowVoltageIcspEntry:
			self.top.hostDelay(self.delayP19)
			self.applyVPP(True)
		self.top.hostDelay(self.delayP7)
		self.sendSIX(0x0, True)
		self.executeCode(self.codeExitResetVectorSimple)
		# self.testPORTA()
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

	def old_readSignature(self):
		self.progressMeterInit("Reading signature", 0)
		self.enterPM()
		self.Image = b""
		self.BufferedBytes = 0
		self.executeCode(self.codeExitResetVector)
		self.executeCode(self.getCodeInitializeTBLPAG(self.deviceIDAddr, 6))
		self.executeCode(self.codeInitializeW7toVISI)
		self.read2words()
		self.progressMeterFinish()
		return self.top.cmdReadBufferReg(4)

	def erase(self):
		self.__erase()

	def __erase(self, keepEEPROM=False):
		def er(NVMCON):
			self.executeCode(self.codeExitResetVector)
			# Set the NVMCON to erase entire PGM
			self.executeCode(self.getCodeSetNVMCON(NVMCON))
			# Set the TBLPAG and perform dummy table write to select the erased memory
			self.executeCode(self.getCodeInitializeTBLPAG(0, 0))
			self.executeCode((0xBB0800, 0x000000, 0x000000))
			# Initiate the erase cycle
			self.executeCode((0xA8E761, 0x000000, 0x000000))
			while self.isWRset():
				pass
		self.progressMeterInit("Erasing chip", 0)
		self.enterPM()
		er(0x4064)
		if(not keepEEPROM and self.eepromPageSize != 0):
			er(0x4050)
		self.progressMeterFinish()
		self.exitPM()

	def readProgmem(self):	
		def unpackImage():
			out = b""
			for halfPackAddr in range(0, len(self.Image), 6):
				out += self.Image[halfPackAddr : halfPackAddr + 3] + b"\0"
				out += self.Image[halfPackAddr + 4 : halfPackAddr + 6]
				out += self.Image[halfPackAddr + 3 : halfPackAddr + 4] + b"\0"
			return out

		nrWords = self.flashPages * self.flashPageSize
		# return self.readSequentialBlock(0x0 , nrWords/2, "Reading Progmem")
		# something wrong for packed PM reading below
		self.enterPM()
		self.progressMeterInit("Reading flash", nrWords // 2)
		self.BufferedBytes = 0
		self.Image = b""
		self.executeCode(self.codeExitResetVector)
		self.executeCode(self.getCodeInitializeTBLPAG(0, 6))
		self.executeCode(self.codeInitializeW7toVISI)
		for wordAddrHalf in range(0, nrWords // 2):
			self.executeCode((0xBA0B96, 0x0, 0x0))
			self.readREGOUTword()
			# Microchip's bug in the documentation
			# TBLRDH.B [W6++], [W7++] is correct instead of TBLRDH [W6++], [W7]
			self.executeCode((0x0, 0xBADBB6, 0x0, 0x0, 0xBAD3D6, 0x0, 0x0))
			self.readREGOUTword()
			self.executeCode((0x0, 0xBA0BB6, 0x0, 0x0))
			self.readREGOUTword()
			self.executeCode(self.codeExitResetVector)
			self.progressMeter(wordAddrHalf)
		self.progressMeterFinish()
		self.flushBufferToImage()
		self.exitPM()
		return unpackImage()

	def _t_readEEPROM(self):	
		nrWords = self.eepromPages * self.eepromPageSize
		self.enterPM()
		self.progressMeterInit("Reading EEPROM", nrWords)
		self.BufferedBytes = 0
		self.Image = b""
		self.executeCode(self.codeExitResetVector)
		self.executeCode(self.getCodeInitializeTBLPAG(0x7F0000 | 0, 6))
		self.executeCode((0x207847, 0x0))
		for wordAddr in range(0, nrWords):
			self.executeCode((0xBA0B96, 0x0, 0x0))
			self.readREGOUTword()
			self.executeCode(self.codeExitResetVector)
			self.progressMeter(wordAddr)
		self.progressMeterFinish()
		self.flushBufferToImage()
		return self.Image

	def readEEPROM(self):
		nrWords = self.eepromPages * self.eepromPageSize
		return self.readSequentialBlock(self.eepromStartAddress , nrWords, "Reading EEPROM")

	def readFuse(self):
		return self.readSequentialBlock(self.configWordAddr, self.fuseBytes // 2, "Reading Config Words")

	def tmp_readSignature(self):
		self.enterPM()
		self.executeCode(self.codeExitResetVector)
		self.executeCode((0x200FF0, 0x880190, 0x200006, 0x0, 0x0, 0x207847, 0x0, 0xBA0BB6, 0x0, 0x0, 0x0))
		self.Image = b""
		self.readREGOUTword()
		self.executeCode(self.codeExitResetVector)
		self.flushBufferToImage()
		signature = self.top.cmdReadBufferReg()[0:2]
		devId = (byte2int(signature[1]) << 8) | byte2int(signature[0])
		if(devId in self.deviceIdMapDict):
			print("device: {:s}".format(self.deviceIdMapDict.get(devId)))
		else:
			print("WARNING: device id {:o} not found in local dictionary".format(devId))
		return self.Image

	def readSignature(self):
		signature = self.readSequentialBlock(self.deviceIDAddr, self.deviceIDLength, "Reading Signature")
		devId = (byte2int(signature[1]) << 8) | byte2int(signature[0])
		if(devId in self.deviceIdMapDict):
			print("device: {:s}".format(self.deviceIdMapDict.get(devId)))
		else:
			print("WARNING: device id {:x} not found in local dictionary".format(devId))
		return signature
		
	def testPORTA(self):
		self.executeCode((0x0, 0x23CFF4, 0x881644, 0x0, 0xEB8200, 0x881654, 0x0, 0x0))

	def readSequentialBlock(self, startAddr, nWords, infoText):	
		self.enterPM()
		self.progressMeterInit(infoText, nWords)
		self.BufferedBytes = 0
		self.Image = b""
		self.executeCode(self.codeExitResetVector)
		self.executeCode(self.getCodeInitializeTBLPAG(startAddr, 6))
		self.executeCode(self.codeInitializeW7toVISI)		
		for wordAddr in range(0, nWords):
			# print "wAddr:{:x}".format(wordAddr)
			self.executeCode((0xBA0BB6, 0x0, 0x0))
			self.readREGOUTword()
			self.executeCode((0x0,))
			self.progressMeter(wordAddr)
		self.executeCode(self.codeExitResetVectorSimple)
		self.progressMeterFinish()
		self.flushBufferToImage()
		self.exitPM()
		return self.Image

	def writeProgmem(self, image):
		def writePackedInstructionWords(addr, _16bytes):
			"""
			writes 4 double word size instructions to program memory.
			Most high instruction byte has 0x00 value and thus is ignored.
			"""
			print("writingPackedInstr init, addr: {:x}\n".format(addr))
			self.executeCode(self.getCodeInitializeTBLPAG(addr, 7))
			cnt = 0
			for wIdx in (0, 8):
			       # LSW0
			       WD = (byte2int(_16bytes[wIdx + 1]) << 8) | byte2int(_16bytes[wIdx + 0])
			       self.executeCode(((0x200000 | (WD << 4) | cnt),))
			       cnt += 1
			       # MSB1 MSB0
			       WD = (byte2int(_16bytes[wIdx + 6]) << 8) | byte2int(_16bytes[wIdx + 2])
			       self.executeCode(((0x200000 | (WD << 4) | cnt),))
			       cnt += 1
			       # LSW1
			       WD = (byte2int(_16bytes[wIdx + 5]) << 8) | byte2int(_16bytes[wIdx + 4])
			       self.executeCode(((0x200000 | (WD << 4) | cnt),))
			       cnt += 1
			self.executeCode((0xEB0300, 0x0))
			print("writingPackedInstr med\n")
			# Set the Read Pointer and load the (next set of) write latches
			for i in range(0, 2):
				self.executeCode((0xBB0BB6, 0x0, 0x0, 0xBBDBB6, 0x0, 0x0, 0xBBEBB6, 0x0, 0x0, 0xBB1BB6, 0x0, 0x0))
			print("writingPackedInstr done\n")
		def writeSeq():
			# Initiate the write cycle
			self.executeCode((0xA8E761, 0x0, 0x0))
			while self.isWRset():
				pass
			self.executeCode((0x040200, 0x0))

		nrWords = self.flashPages * self.flashPageSize
		if len(image) > (nrWords * 4) or len(image) % 4 != 0:
			self.throwError("Invalid flash image size %d (expected <=%d and double word aligned)" % \
				(len(image), nrWords * 4))
		self.progressMeterInit("Writing flash", len(image) // 12)
		self.enterPM()
		self.executeCode(self.codeExitResetVector)
		self.executeCode(self.getCodeSetNVMCON(0x4004))
		for packAddr in range(0, len(image) // 16):
			self.progressMeter(packAddr)
			writePackedInstructionWords(packAddr * 8, image[16 * packAddr:][:16])
			if(0 == ((packAddr + 1) % 8)):
				writeSeq()
		writeSeq()
		self.progressMeterFinish()
		self.exitPM()

	def writeEEPROM(self, image):
		nrWords = self.eepromPages * self.eepromPageSize
		if len(image) > nrWords * 2:
			self.throwError("Invalid flash image size {:d} (expected <={:d})".format(len(image), 2 * nrWords))
		self.enterPM()
		self.progressMeterInit("Writing eeprom", len(image) // 2)
		self.executeCode(self.codeExitResetVector)
		self.executeCode(self.getCodeSetNVMCON(0x4004))
		for addr in range(0, len(image) // 2):
			self.progressMeter(addr)
			WD = (byte2int(image[addr * 2 + 1]) << 8) | byte2int(image[addr * 2 + 0])
			if WD != 0xFFFF:
				self.executeCode(self.getCodeInitializeTBLPAG(self.eepromStartAddress | (2 * addr), 7))
				# Load W0 with data word program and load the wire latch 
				self.executeCode((0x200000 | (WD << 4), 0xBB1B80, 0x0, 0x0))
				# Initiate the write cycle
				self.executeCode((0xA8E761, 0x0, 0x0))
				while self.isWRset():
					pass
				self.executeCode(self.codeExitResetVectorSimple)
				
				
		self.progressMeterFinish()
		self.exitPM()
		
	def writeFuse(self, image):
		if len(image) != self.fuseBytes:
			self.throwError("Invalid Fuses image size %d (expected %d)" % \
				(len(image), self.fuseBytes))
		self.progressMeterInit("Writing fuses", 0)
		# print "image1:%x,,%x,,%x" % (byte2int(image[0]),byte2int(image[1]),byte2int(image[1])<<8)
		CW = []
		for tBytes in zip(image[::2], image[1::2]):
			CW.append((byte2int(tBytes[1]) << 8) | byte2int(tBytes[0]))
		self.writeConfigWord(CW)
		self.progressMeterFinish()
    
	def writeConfigWord(self, listConfigWord16):
		self.enterPM()
		self.executeCode(self.codeExitResetVector)
		# init WritePointer (W7) for the TBLWT instruction, Set the NVMCON reg. to prog. Config. regs.
		self.executeCode((0x200007, 0x24004A, 0x883B0A))
		# init TBLPAG
		# another bug in Microchip's doc  - s/0x200F86/0x200F80/
		self.executeCode((0x200F80, 0x880190))
		for configWord16 in listConfigWord16:
			print("write CW 0x{:x}".format(configWord16))
			# Load the Config reg data to W6
			self.executeCode(((0x200006 | (configWord16 << 4)),))
			# Write the Config. reg. data to the write latch and increment Write Pointer
			self.executeCode((0x0, 0xBB1B86, 0x0, 0x0))
			# Initiate the write cycle
			self.executeCode((0xA8E761, 0x0, 0x0))
			while self.isWRset():
				pass
			self.executeCode(self.codeExitResetVectorSimple)
		self.top.flushCommands()
		self.progressMeterFinish()

	def exitPM(self):
		"Exit programming mode. Vdd last exit mode"
		self.top.flushCommands()
		self.setPins(0, 0)
		self.top.hostDelay(self.delayP16)
		self.applyVPP(False)
		self.top.hostDelay(self.delayP17)
		self.applyVCC(False)
		self.applyGND(False)
		self.isInPmMode = False

	def setSDI(self, sdi):
		'''
		16 -set 24 bit sdi value
		'''
		for addr in (0x13, 0x14, 0x15):
			self.top.cmdFPGAWrite(addr, sdi & 0xFF)
			sdi = sdi >> 8

	def sendCommand(self, command):
		'''
		16 - send command
		CMD_SENDSIXINSTR	0
		CMD_SENDREGOUTINSTR	1
		CMD_ENTERPM 2
		'''
		self.top.cmdFPGAWrite(0x12, command)

	def readREGOUTword(self):
		def incBbAndCheckFillImage():
			self.BufferedBytes += 1
			if self.BufferedBytes == self.top.getBufferRegSize():
				self.Image += self.top.cmdReadBufferReg(self.BufferedBytes)
				self.BufferedBytes = 0
		self.busyWait()
		# self.top.hostDelay(0.000001)
		self.sendCommand(self.PROGCMD_SENDREGOUTINSTR)
		self.busyWait()
		# self.top.hostDelay(0.000001)
		self.readSDOBufferLow()
		incBbAndCheckFillImage()
		self.readSDOBufferHigh()
		incBbAndCheckFillImage()

	def flushBufferToImage(self):
		if self.BufferedBytes > 0:
			self.Image += self.top.cmdReadBufferReg(self.BufferedBytes)
			self.BufferedBytes = 0

	def sendSIX(self, instr, is9SIX=False):
		self.busyWait()		
		self.setSDI(instr)
		self.sendCommand((self.PROGCMD_SENDSIXINSTR, self.PROGCMD_SEND9SIXINSTR)[is9SIX])

	def read2words(self):
		self.executeCode((0xBA0B96, 0x000000, 0x000000))
		self.readREGOUTword()
		self.executeCode((0x0000000, 0xBA8BB6, 0x000000, 0x000000, 0xBAD3D6, 0x000000, 0x000000))
		self.readREGOUTword()
		self.executeCode((0x000000, 0xBA0BB6, 0x000000, 0x000000))
		self.readREGOUTword()
		self.executeCode((0x000000,))

	def executeCode(self, code):
		for instr in code:
			self.sendSIX(instr)

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
		self.top.cmdFPGAWrite(0x19, data)

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
		self.top.cmdFPGARead(0x10)

	def readSDOBufferLow(self):
		self.top.cmdFPGARead(0x13)	

	def rawSDIOState(self):
		return bool(self.getStatusFlags() & self.STAT_SDIO)

	def isBusy(self):
		return bool(self.getStatusFlags() & self.STAT_BUSY)

	def setTopProgrammerDelays(self):
		# print("tdel5:{:d}".format(int(math.ceil(self.delayP3 / 42e-9))))
		# print("tdly:{:d}".format(int(math.ceil(self.delayCommandDataREGOUT / 42e-9))))
		self.top.cmdFPGAWrite(0x10, int(math.ceil(self.delayP3 / 42e-9)))
		self.top.cmdFPGAWrite(0x11, int(math.ceil(self.delayCommandDataREGOUT / 42e-9)))

	def busyWait(self):
		# We do not poll the busy flag, because that would result
		# in a significant slowdown. We delay long enough for the
		# command to finish execution, instead.
		self.top.hostDelay(0.0000005)
		return
		for i in range(0, 100):
			if not self.isBusy():
				return
			self.top.hostDelay(0.000001)
		self.throwError("Timeout in busywait.")	

	def getCodeInitializeTBLPAG(self, addr, wIdx=0):
		mlw = (addr & 0xFFFF) << 4
		mmb = (addr >> 12) & 0x000FF0
		return (0x200000 | mmb, 0x880190, 0x200000 | mlw | (wIdx & 0x0F))

	def getCodeSetNVMCON(self, NVMCON):
		return (0x20000A | ((NVMCON & 0xFFFF) << 4), 0x883B0A)

	def isWRset(self):
		self.executeCode(self.codeExitResetVectorSimple)
		self.executeCode((0x803B02, 0x883C22, 0x000000))
		self.BufferedBytes = 0
		self.Image = b""
		self.readREGOUTword()
		self.flushBufferToImage()
		self.executeCode((0x000000,))
		return byte2int(self.Image[1]) & 0x80
