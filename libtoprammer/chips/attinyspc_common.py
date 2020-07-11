"""
#    TOP2049 Open Source programming suite
#
#    Atmel Tiny small pin count
#
#    Copyright (c) 2010 Michael Buesch <m@bues.ch>
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


class Chip_AtTinySPC_common(Chip):
	PROGCMD_SENDINSTR	= 1 # Send an instruction to the chip

	STAT_BUSY		= 0x01 # Programmer is running a command
	STAT_SDO		= 0x02 # Raw SDO pin state

	def __init__(self,
		     chipPackage,
		     chipPinVCC,
		     chipPinsVPP,
		     chipPinGND,
		     signature,
		     flashPageSize,
		     flashPages,
		     eepromPageSize,
		     eepromPages,
		     nrFuseBits,
		     nrLockBits):
		Chip.__init__(self,
			      chipPackage=chipPackage,
			      chipPinVCC=chipPinVCC,
			      chipPinsVPP=chipPinsVPP,
			      chipPinGND=chipPinGND)
		self.signature = signature
		self.flashPageSize = flashPageSize
		self.flashPages = flashPages
		self.eepromPageSize = eepromPageSize
		self.eepromPages = eepromPages
		self.nrFuseBits = nrFuseBits
		self.nrLockBits = nrLockBits

	def readSignature(self):
		self.__enterPM()
		self.progressMeterInit("Reading signature", 0)
		signature = self.__readSignature()
		self.progressMeterFinish()
		return signature

	def erase(self):
		self.__enterPM()
		self.progressMeterInit("Erasing chip", 0)
		self.__sendInstr(SDI=0x80, SII=0x4C)
		self.__sendInstr(SDI=0x00, SII=0x64)
		self.__sendInstr(SDI=0x00, SII=0x6C)
		self.__waitHighSDO()
		self.__sendNOP()
		self.progressMeterFinish()

	def readProgmem(self):
		nrWords = self.flashPages * self.flashPageSize
		image = b""
		self.__enterPM()
		self.progressMeterInit("Reading flash", nrWords)
		self.__sendReadFlashInstr()
		currentHigh = -1
		bufferedBytes = 0
		for word in range(0, nrWords):
			self.progressMeter(word)
			low = word & 0xFF
			high = (word >> 8) & 0xFF
			self.__sendInstr(SDI=low, SII=0x0C)
			if high != currentHigh:
				self.__sendInstr(SDI=high, SII=0x1C)
				currentHigh = high
			self.__sendInstr(SDI=0x00, SII=0x68)
			self.__sendInstr(SDI=0x00, SII=0x6C)
			self.__readSDOBufferHigh()
			bufferedBytes += 1
			self.__sendInstr(SDI=0x00, SII=0x78)
			self.__sendInstr(SDI=0x00, SII=0x7C)
			self.__readSDOBufferHigh()
			bufferedBytes += 1
			if bufferedBytes == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(bufferedBytes)
				bufferedBytes = 0
		image += self.top.cmdReadBufferReg(bufferedBytes)
		self.progressMeterFinish()
		return image

	def writeProgmem(self, image):
		nrWords = self.flashPages * self.flashPageSize
		if len(image) > nrWords * 2 or len(image) % 2 != 0:
			self.throwError("Invalid flash image size %d (expected <=%d and word aligned)" %\
				(len(image), nrWords * 2))
		self.__enterPM()
		self.progressMeterInit("Writing flash", len(image) // 2)
		self.__sendWriteFlashInstr()
		currentHigh = -1
		for word in range(0, len(image) // 2):
			self.progressMeter(word)
			low = word & 0xFF
			high = (word >> 8) & 0xFF
			self.__sendInstr(SDI=low, SII=0x0C)
			self.__sendInstr(SDI=byte2int(image[word * 2 + 0]), SII=0x2C)
			self.__sendInstr(SDI=byte2int(image[word * 2 + 1]), SII=0x3C)
			self.__sendInstr(SDI=0x00, SII=0x7D)
			self.__sendInstr(SDI=0x00, SII=0x7C)
			if ((word + 1) % self.flashPageSize == 0) or word == len(image) // 2 - 1:
				if currentHigh != high:
					self.__sendInstr(SDI=high, SII=0x1C)
					currentHigh = high
				self.__sendInstr(SDI=0x00, SII=0x64)
				self.__sendInstr(SDI=0x00, SII=0x6C)
				self.__waitHighSDO()
		self.__sendNOP()
		self.progressMeterFinish()

	def readEEPROM(self):
		nrBytes = self.eepromPages * self.eepromPageSize
		image = b""
		self.__enterPM()
		self.progressMeterInit("Reading EEPROM", nrBytes)
		self.__sendReadEEPROMInstr()
		currentPage = -1
		bufferedBytes = 0
		for i in range(0, nrBytes):
			self.progressMeter(i)
			low = i & 0xFF
			high = (i >> 8) & 0xFF
			self.__sendInstr(SDI=low, SII=0x0C)
			if currentPage != high:
				self.__sendInstr(SDI=high, SII=0x1C)
				currentPage = high
			self.__sendInstr(SDI=0x00, SII=0x68)
			self.__sendInstr(SDI=0x00, SII=0x6C)
			self.__readSDOBufferHigh()
			bufferedBytes += 1
			if bufferedBytes == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(bufferedBytes)
				bufferedBytes = 0
		image += self.top.cmdReadBufferReg(bufferedBytes)
		self.progressMeterFinish()
		return image

	def writeEEPROM(self, image):
		nrBytes = self.eepromPages * self.eepromPageSize
		if len(image) > nrBytes:
			self.throwError("Invalid EEPROM image size %d (expected <=%d)" %\
				(len(image), nrBytes))
		self.__enterPM()
		self.progressMeterInit("Writing EEPROM", len(image))
		self.__sendWriteEEPROMInstr()
		for i in range(0, len(image)):
			self.progressMeter(i)
			low = i & 0xFF
			high = (i >> 8) & 0xFF
			self.__sendInstr(SDI=low, SII=0x0C)
			self.__sendInstr(SDI=high, SII=0x1C)
			self.__sendInstr(SDI=byte2int(image[i]), SII=0x2C)
			self.__sendInstr(SDI=0x00, SII=0x6D)
			self.__sendInstr(SDI=0x00, SII=0x64)
			self.__sendInstr(SDI=0x00, SII=0x6C)
			self.__waitHighSDO()
		self.__sendNOP()
		self.progressMeterFinish()

	def readFuse(self):
		usedBitsMask = (1 << self.nrFuseBits) - 1
		unusedBitsMask = usedBitsMask ^ 0xFFFFFF
		fuses = []
		self.__enterPM()
		self.progressMeterInit("Reading fuses", 0)
		self.__sendInstr(SDI=0x04, SII=0x4C)
		self.__sendInstr(SDI=0x00, SII=0x68)
		self.__sendInstr(SDI=0x00, SII=0x6C)
		self.__readSDOBufferHigh()
		fuses.append(int2byte(self.top.cmdReadBufferReg8() |
				      ((unusedBitsMask >> 0) & 0xFF)))
		if self.nrFuseBits > 8:
			self.__sendInstr(SDI=0x04, SII=0x4C)
			self.__sendInstr(SDI=0x00, SII=0x7A)
			self.__sendInstr(SDI=0x00, SII=0x7E)
			self.__readSDOBufferHigh()
			fuses.append(int2byte(self.top.cmdReadBufferReg8() |
					      ((unusedBitsMask >> 8) & 0xFF)))
		if self.nrFuseBits > 16:
			self.__sendInstr(SDI=0x04, SII=0x4C)
			self.__sendInstr(SDI=0x00, SII=0x6A)
			self.__sendInstr(SDI=0x00, SII=0x6E)
			self.__readSDOBufferHigh()
			fuses.append(int2byte(self.top.cmdReadBufferReg8() |
					      ((unusedBitsMask >> 16) & 0xFF)))
		self.progressMeterFinish()
		return b"".join(fuses)

	def writeFuse(self, image):
		if len(image) != roundup(self.nrFuseBits, 8) // 8:
			self.throwError("Invalid Fuses image size %d (expected %d)" %\
				(len(image), roundup(self.nrFuseBits, 8) // 8))
		usedBitsMask = (1 << self.nrFuseBits) - 1
		self.__enterPM()
		self.progressMeterInit("Writing fuses", 0)
		self.__sendInstr(SDI=0x40, SII=0x4C)
		self.__sendInstr(SDI=(image[0] & (usedBitsMask >> 0)), SII=0x2C)
		self.__sendInstr(SDI=0x00, SII=0x64)
		self.__sendInstr(SDI=0x00, SII=0x6C)
		self.__waitHighSDO()
		if self.nrFuseBits > 8:
			self.__sendInstr(SDI=0x40, SII=0x4C)
			self.__sendInstr(SDI=(image[1] & (usedBitsMask >> 8)), SII=0x2C)
			self.__sendInstr(SDI=0x00, SII=0x74)
			self.__sendInstr(SDI=0x00, SII=0x7C)
			self.__waitHighSDO()
		if self.nrFuseBits > 16:
			self.__sendInstr(SDI=0x40, SII=0x4C)
			self.__sendInstr(SDI=(image[2] & (usedBitsMask >> 16)), SII=0x2C)
			self.__sendInstr(SDI=0x00, SII=0x66)
			self.__sendInstr(SDI=0x00, SII=0x6E)
			self.__waitHighSDO()
		self.progressMeterFinish()

	def readLockbits(self):
		usedBitsMask = (1 << self.nrLockBits) - 1
		unusedBitsMask = usedBitsMask ^ 0xFF
		self.__enterPM()
		self.progressMeterInit("Reading lockbits", 0)
		self.__sendInstr(SDI=0x04, SII=0x4C)
		self.__sendInstr(SDI=0x00, SII=0x78)
		self.__sendInstr(SDI=0x00, SII=0x7C)
		self.__readSDOBufferHigh()
		lockbits = int2byte(self.top.cmdReadBufferReg8() | unusedBitsMask)
		self.progressMeterFinish()
		return lockbits

	def writeLockbits(self, image):
		if len(image) != roundup(self.nrLockBits, 8) // 8:
			self.throwError("Invalid Lockbits image size %d (expected %d)" %\
				(len(image), roundup(self.nrLockBits, 8) // 8))
		usedBitsMask = (1 << self.nrLockBits) - 1
		self.__enterPM()
		self.progressMeterInit("Writing lockbits", 0)
		self.__sendInstr(SDI=0x20, SII=0x4C)
		self.__sendInstr(SDI=(byte2int(image[0]) & usedBitsMask), SII=0x2C)
		self.__sendInstr(SDI=0x00, SII=0x64)
		self.__sendInstr(SDI=0x00, SII=0x6C)
		self.__waitHighSDO()
		self.progressMeterFinish()

	def __readSignature(self):
		self.__sendInstr(SDI=0x08, SII=0x4C)
		for i in range(0, 3):
			self.__sendInstr(SDI=i, SII=0x0C)
			self.__sendInstr(SDI=0x00, SII=0x68)
			self.__sendInstr(SDI=0x00, SII=0x6C)
			self.__readSDOBufferHigh()
		return self.top.cmdReadBufferReg()[0:3]

	def __enterPM(self):
		"Enter HV programming mode."
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.top.cmdSetVCCVoltage(5)
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(12)
		self.applyGND(True)
		self.applyVCC(True)

		self.__setPins(SCI=0, SDO_en=0, RST_en=1, RST=0)
		for i in range(0, 6):
			self.__setPins(SCI=0, SDO_en=0, RST_en=1, RST=0)
			self.__setPins(SCI=1, SDO_en=0, RST_en=1, RST=0)
		self.__setPins(SCI=0, SDO_en=1, SDO=0, RST_en=1, RST=0)
		self.top.hostDelay(0.001)
		self.__setPins(SDO_en=1, SDO=0, RST_en=0)
		self.applyVPP(True)
		self.top.hostDelay(0.001)
		self.__setPins(SDO_en=0)
		self.top.hostDelay(0.01)

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

	def __sendReadEEPROMInstr(self):
		self.__sendInstr(SDI=0x03, SII=0x4C)

	def __sendWriteEEPROMInstr(self):
		self.__sendInstr(SDI=0x11, SII=0x4C)

	def __sendReadFlashInstr(self):
		self.__sendInstr(SDI=0x02, SII=0x4C)

	def __sendWriteFlashInstr(self):
		self.__sendInstr(SDI=0x10, SII=0x4C)

	def __sendNOP(self):
		self.__sendInstr(SDI=0x00, SII=0x4C)

	def __sendInstr(self, SDI, SII):
		self.__setSDI(SDI)
		self.__setSII(SII)
		self.__loadCommand(self.PROGCMD_SENDINSTR)
		# We do not poll the busy flag, because that would result
		# in a significant slowdown. We delay long enough for the
		# command to finish execution, instead.
		self.top.hostDelay(0.001)

	def __setSDI(self, sdi):
		self.top.cmdFPGAWrite(0x13, sdi & 0xFF)

	def __setSII(self, sii):
		self.top.cmdFPGAWrite(0x14, sii & 0xFF)

	def __loadCommand(self, command):
		self.top.cmdFPGAWrite(0x12, command & 0xFF)

	def __runCommandSync(self, command):
		self.__loadCommand(command)
		self.__busyWait()

	def __setPins(self, SCI=0, SDO_en=0, SDO=0, RST_en=0, RST=0):
		data = 0
		if SCI:
			data |= 1
		if SDO_en:
			data |= 2
		if SDO:
			data |= 4
		if RST_en:
			data |= 8
		if RST:
			data |= 16
		self.top.cmdFPGAWrite(0x15, data)

	def __getStatusFlags(self):
		self.top.cmdFPGARead(0x12)
		stat = self.top.cmdReadBufferReg()
		return byte2int(stat[0])

	def __readSDOBufferHigh(self):
		self.top.cmdFPGARead(0x10)

	def __rawSDOState(self):
		return bool(self.__getStatusFlags() & self.STAT_SDO)

	def __busy(self):
		return bool(self.__getStatusFlags() & self.STAT_BUSY)

	def __busyWait(self):
		for i in range(0, 100):
			if not self.__busy():
				return
			self.top.hostDelay(0.01)
		self.throwError("Timeout in busywait.")

	def __waitHighSDO(self):
		for i in range(0, 100):
			if self.__rawSDOState():
				return
			self.top.hostDelay(0.01)
		self.throwError("Timeout waiting for SDO.")
