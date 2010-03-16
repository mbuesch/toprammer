"""
#    TOP2049 Open Source programming suite
#
#    Implements the Atmel Mega MCU parallel HV programming algorithm
#
#    Copyright (c) 2009-2010 Michael Buesch <mb@bu3sch.de>
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

from chip import *


class Chip_ATMega_common(Chip):
	# The Atmel Mega programming commands
	CMD_CHIPERASE		= 0x80 # Chip Erase
	CMD_WRITEFUSE		= 0x40 # Write Fuse Bits
	CMD_WRITELOCK		= 0x20 # Write Lock Bits
	CMD_WRITEFLASH		= 0x10 # Write Flash
	CMD_WRITEEEPROM		= 0x11 # Write EEPROM
	CMD_READSIG		= 0x08 # Read Signature bytes and Calibration byte
	CMD_READFUSELOCK	= 0x04 # Read Fuse and Lock bits
	CMD_READFLASH		= 0x02 # Read Flash
	CMD_READEEPROM		= 0x03 # Read EEPROM

	def __init__(self,
		     chipPackage, chipPinVCCX, chipPinsVPP, chipPinGND,
		     signature,
		     flashPageSize, flashPages,
		     eepromPageSize, eepromPages
		    ):
		Chip.__init__(self,
			      chipPackage = chipPackage,
			      chipPinVCCX = chipPinVCCX,
			      chipPinsVPP = chipPinsVPP,
			      chipPinGND = chipPinGND)
		self.signature = signature
		self.flashPageSize = flashPageSize	# Flash page size, in words
		self.flashPages = flashPages		# Nr of flash pages
		self.eepromPageSize = eepromPageSize	# EEPROM page size, in bytes
		self.eepromPages = eepromPages		# Nr of EEPROM pages
		assert(eepromPageSize <= 64)

	def initializeChip(self):
		self.printDebug("Initializing chip")
		self.applyGND(True)
		self.applyVCCX(False)
		self.applyVPP(False)
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(12)

	def shutdownChip(self):
		self.printDebug("Shutdown chip")
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(5)
		self.applyVCCX(False)
		self.applyVPP(False)
		self.applyGND(False)

	def readSignature(self):
		self.__initPins()

		(signature, calibration) = self.__readSigAndCalib()

		return signature

	def erase(self):
		self.__initPins()

		self.progressMeterInit("Erasing chip", 0)
		self.__loadCommand(self.CMD_CHIPERASE)
		self.__pulseWR()
		self.__waitForRDY()
		self.progressMeterFinish()

	def readProgmem(self):
		self.__initPins()

		self.progressMeterInit("Reading Flash", self.flashPages)
		image = ""
		for page in range(0, self.flashPages):
			self.progressMeter(page)
			readWords = 0
			for word in range(0, self.flashPageSize):
				self.__loadCommand(self.CMD_READFLASH)
				self.__loadAddr((page * self.flashPageSize) + word)
				self.__readWordToStatusReg()
				readWords += 1
				if readWords >= 32:
					image += self.top.cmdReadStatusReg()
					readWords = 0
			if readWords:
				data = self.top.cmdReadStatusReg()
				image += data[0:readWords*2]
		self.progressMeterFinish()
		return image

	def writeProgmem(self, image):
		flashBytes = self.flashPageSize * 2 * self.flashPages
		if len(image) != flashBytes:
			self.throwError("Invalid program memory image size %d (expected %d)" %\
				(len(image), flashBytes))
		self.__initPins()

		self.progressMeterInit("Writing Flash", self.flashPages)
		for page in range(0, self.flashPages):
			self.progressMeter(page)
			for word in range(0, self.flashPageSize):
				self.__loadCommand(self.CMD_WRITEFLASH)
				addr = (page * self.flashPageSize) + word
				self.__loadAddr(addr)
				addr *= 2
				data = image[addr : addr + 2]
				self.__loadData(ord(data[0]) | (ord(data[1]) << 8))
				self.__setBS1(1)
				self.__pulsePAGEL()
			self.__setBS1(0)
			self.__pulseWR()
			self.__waitForRDY()
		self.progressMeterFinish()

	def readEEPROM(self):
		self.__initPins()

		self.progressMeterInit("Reading EEPROM", self.eepromPages)
		image = ""
		for page in range(0, self.eepromPages):
			self.progressMeter(page)
			for byte in range(0, self.eepromPageSize):
				self.__loadCommand(self.CMD_READEEPROM)
				self.__loadAddr((page * self.eepromPageSize) + byte)
				self.__readLowByteToStatusReg()
			data = self.top.cmdReadStatusReg()
			image += data[0:self.eepromPageSize]
		self.progressMeterFinish()
		return image

	def writeEEPROM(self, image):
		eepromBytes = self.eepromPageSize * self.eepromPages
		if len(image) != eepromBytes:
			self.throwError("Invalid EEPROM image size %d (expected %d)" %\
				(len(image), eepromBytes))
		self.__initPins()

		self.progressMeterInit("Writing EEPROM", self.eepromPages)
		for page in range(0, self.eepromPages):
			self.progressMeter(page)
			for byte in range(0, self.eepromPageSize):
				self.__loadCommand(self.CMD_WRITEEEPROM)
				addr = (page * self.eepromPageSize) + byte
				self.__loadAddr(addr)
				data = image[addr]
				self.__loadDataLow(ord(data[0]))
				self.__pulsePAGEL()
			self.__setBS1(0)
			self.__pulseWR()
			self.__waitForRDY()
		self.progressMeterFinish()

	def readFuse(self):
		self.__initPins()

		self.progressMeterInit("Reading Fuse bits", 0)
		(fuse, lock) = self.__readFuseAndLockBits()
		self.progressMeterFinish()
		return fuse

	def writeFuse(self, image):
		if len(image) != 2:
			self.throwError("Invalid Fuses image size %d (expected %d)" %\
				(len(image), 2))
		self.__initPins()

		self.progressMeterInit("Writing Fuse bits", 0)
		self.__loadCommand(self.CMD_WRITEFUSE)
		self.__setBS2(0)
		self.__loadDataLow(ord(image[0]))
		self.__pulseWR()
		self.__waitForRDY()
		self.__loadCommand(self.CMD_WRITEFUSE)
		self.__loadDataLow(ord(image[1]))
		self.__setBS1(1)
		self.__pulseWR()
		self.__waitForRDY()
		self.progressMeterFinish()

	def readLockbits(self):
		self.__initPins()

		self.progressMeterInit("Reading lock bits", 0)
		(fuses, lockbits) = self.__readFuseAndLockBits()
		self.progressMeterFinish()

		return lockbits

	def writeLockbits(self, image):
		if len(image) != 1:
			self.throwError("Invalid lock-bits image size %d (expected %d)" %\
				(len(image), 1))
		self.__initPins()

		self.progressMeterInit("Writing lock bits", 0)
		self.__loadCommand(self.CMD_WRITELOCK)
		self.__loadDataLow(ord(image[0]))
		self.__pulseWR()
		self.__waitForRDY()
		self.progressMeterFinish()

	def __readSigAndCalib(self):
		"""Reads the signature and calibration bytes and returns them.
		This function expects a DUT present and pins initialized."""
		signature = ""
		calibration = ""
		for addr in range(0, 4):
			self.__loadCommand(self.CMD_READSIG)
			self.__loadAddr(addr)
			self.__readWordToStatusReg()
			data = self.top.cmdReadStatusReg()
			if addr <= 2:
				signature += data[0]
			calibration += data[1]
		return (signature, calibration)

	def __readFuseAndLockBits(self):
		"""Reads the Fuse and Lock bits and returns them.
		This function expects a DUT present and pins initialized."""
		self.__loadCommand(self.CMD_READFUSELOCK)
		self.__setBS2(0)
		self.__readWordToStatusReg()
		self.__setBS2(1)
		self.__readWordToStatusReg()
		self.__setBS2(0)
		data = self.top.cmdReadStatusReg()
		fuses = data[0] + data[3]
		lock = data[1]
		return (fuses, lock)

	def __initPins(self):
		"""Initialize the pin voltages and logic."""
		self.applyVPP(False)
		self.applyVCCX(False)
		self.top.queueCommand("\x0E\x28\x00\x00")
		self.top.cmdFPGAWrite(0x1B, 0x00)
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(12)
		self.applyGND(True)
		self.top.cmdSetVCCXVoltage(4.4)

		self.__setXA0(0)
		self.__setXA1(0)
		self.__setBS1(0)
		self.__setWR(0)
		self.top.flushCommands()

		self.applyGND(True)
		self.applyVCCX(True)

		self.top.queueCommand("\x19")
		self.__setReadMode(0)
		self.top.queueCommand("\x34")
		self.__setReadMode(0)
		self.__setOE(0)
		self.__setWR(1)
		self.__setXTAL1(0)
		self.__setXA0(0)
		self.__setXA1(0)
		self.top.cmdFPGAWrite(0x12, 0x08)
		self.__setBS1(0)
		self.__setBS2(0)
		self.__setPAGEL(0)
		self.__pulseXTAL1(10)
		self.top.queueCommand("\x19")
		self.top.flushCommands()

		self.applyVPP(True)
		self.top.queueCommand("\x0E\x28\x01\x00")

		self.top.queueCommand("\x34")
		self.top.cmdFPGAWrite(0x12, 0x88)
		self.__setOE(1)
		self.top.cmdFlush()

		(signature, calibration) = self.__readSigAndCalib()
		if signature != self.signature:
			msg = "Unexpected device signature. " +\
			      "Want %02X%02X%02X, but got %02X%02X%02X" % \
				(ord(self.signature[0]), ord(self.signature[1]),
				 ord(self.signature[2]),
				 ord(signature[0]), ord(signature[1]),
				 ord(signature[2]))
			if self.top.getForceLevel() >= 1:
				self.printWarning(msg)
			else:
				self.throwError(msg)

		self.top.cmdFlush(10)
		self.top.queueCommand("\x0E\x1F\x00\x00")
		self.top.delay(0.1)
		stat = self.top.cmdReadStatusReg32()
		if stat != 0xB9C80101:
			self.throwError("read: Unexpected status value 0x%08X" % stat)

	def __readWordToStatusReg(self):
		"""Read a data word from the DUT into the status register."""
		self.__setReadMode(1)
		self.__setBS1(0)
		self.__setOE(0)
		self.top.cmdFPGAReadByte()
		self.__setBS1(1)
		self.top.cmdFPGAReadByte()
		self.__setOE(1)
		self.__setReadMode(0)

	def __readLowByteToStatusReg(self):
		"""Read the low data byte from the DUT into the status register."""
		self.__setReadMode(1)
		self.__setBS1(0)
		self.__setOE(0)
		self.top.cmdFPGAReadByte()
		self.__setOE(1)
		self.__setReadMode(0)

	def __readHighByteToStatusReg(self):
		"""Read the high data byte from the DUT into the status register."""
		self.__setReadMode(1)
		self.__setBS1(1)
		self.__setOE(0)
		self.top.cmdFPGAReadByte()
		self.__setOE(1)
		self.__setReadMode(0)

	def __loadData(self, data):
		"""Load a data word."""
		self.__loadDataLow(data)
		self.__loadDataHigh(data >> 8)

	def __loadDataLow(self, dataLow):
		"""Load the low data byte."""
		self.__setBS1(0)
		self.__setXA0(1)
		self.__setXA1(0)
		self.top.cmdFPGAWrite(0x10, dataLow & 0xFF)
		self.__pulseXTAL1()

	def __loadDataHigh(self, dataHigh):
		"""Load the high data byte."""
		self.__setBS1(1)
		self.__setXA0(1)
		self.__setXA1(0)
		self.top.cmdFPGAWrite(0x10, dataHigh & 0xFF)
		self.__pulseXTAL1()

	def __loadAddr(self, addr):
		"""Load an address word."""
		self.__loadAddrLow(addr)
		self.__loadAddrHigh(addr >> 8)

	def __loadAddrLow(self, addrLow):
		"""Load the low address byte."""
		self.__setBS1(0)
		self.__setXA0(0)
		self.__setXA1(0)
		self.top.cmdFPGAWrite(0x10, addrLow & 0xFF)
		self.__pulseXTAL1()

	def __loadAddrHigh(self, addrHigh):
		"""Load the high address byte."""
		self.__setBS1(1)
		self.__setXA0(0)
		self.__setXA1(0)
		self.top.cmdFPGAWrite(0x10, addrHigh & 0xFF)
		self.__pulseXTAL1()

	def __loadCommand(self, command):
		"""Load a command into the device."""
		self.top.queueCommand("\x34")
		self.__setBS1(0)
		self.top.queueCommand("\x34")
		self.__setXA0(0)
		self.__setXA1(1)
		self.top.cmdFPGAWrite(0x10, command)
		self.__pulseXTAL1()

	def __setReadMode(self, high):
		"""Put the FPGA into read mode."""
		value = 0x01
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __waitForRDY(self):
		"""Wait for the RDY pin to go high."""
		self.top.delay(0.01)
		for i in range(0, 50):
			if self.__getRDY():
				return
			self.top.delay(0.01)
		self.throwError("Timeout waiting for READY signal from chip.")

	def __getRDY(self):
		"""Read the state of the RDY/BSY pin."""
		return bool(self.__getStatus() & 0x01)

	def __getStatus(self):
		"""Read the programmer status register"""
		self.top.cmdFPGAReadRaw(0x12)
		stat = self.top.cmdReadStatusReg()
		return ord(stat[0])

	def __setOE(self, high):
		"""Set the OE pin of the DUT"""
		value = 0x02
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __setWR(self, high):
		"""Set the WR pin of the DUT"""
		value = 0x03
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __pulseWR(self, count=1):
		"""Do a negative pulse on the WR pin of the DUT"""
		while count > 0:
			self.__setWR(0)
			self.__setWR(1)
			count -= 1

	def __setBS1(self, high):
		"""Set the BS1 pin of the DUT"""
		value = 0x04
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __setXA0(self, high):
		"""Set the XA0 pin of the DUT"""
		value = 0x05
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __setXA1(self, high):
		"""Set the XA1 pin of the DUT"""
		value = 0x06
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __setXTAL1(self, high):
		"""Set the XTAL1 pin of the DUT"""
		value = 0x07
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __pulseXTAL1(self, count=1):
		"""Do a positive pulse on the XTAL1 pin of the DUT"""
		while count > 0:
			self.__setXTAL1(1)
			self.__setXTAL1(0)
			count -= 1

	def __setPAGEL(self, high):
		"""Set the PAGEL pin of the DUT"""
		value = 0x09
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)

	def __pulsePAGEL(self, count=1):
		"""Do a positive pulse on the PAGEL pin of the DUT"""
		while count > 0:
			self.__setPAGEL(1)
			self.__setPAGEL(0)
			count -= 1

	def __setBS2(self, high):
		"""Set the BS2 pin of the DUT"""
		value = 0x0A
		if high:
			value |= 0x80
		self.top.cmdFPGAWrite(0x12, value)
