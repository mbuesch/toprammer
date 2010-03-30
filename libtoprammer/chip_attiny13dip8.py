"""
#    TOP2049 Open Source programming suite
#
#    Atmel Tiny13 DIP8
#
#    Copyright (c) 2010 Michael Buesch <mb@bu3sch.de>
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


class Chip_AtTiny13dip8(Chip):
	PROGCMD_SENDINSTR	= 1 # Send an instruction to the chip

	STAT_BUSY		= 0x01 # Programmer is running a command
	STAT_SDO		= 0x02 # Raw SDO pin state

	def __init__(self):
		Chip.__init__(self,
			      chipPackage = "DIP8",
			      chipPinVCCX = 8,
			      chipPinsVPP = 1,
			      chipPinGND = 4)
		self.signature = "\x1E\x90\x07"

	def initializeChip(self):
		self.printDebug("Initializing chip")
		self.applyVCCX(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.top.queueCommand("\x0E\x28\x00\x00")
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(5)

	def shutdownChip(self):
		self.printDebug("Shutdown chip")
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(5)
		self.applyVCCX(False)
		self.applyVPP(False)
		self.applyGND(False)

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
		pass#TODO

	def writeProgmem(self, image):
		pass#TODO

	def readEEPROM(self):
		pass#TODO

	def writeEEPROM(self, image):
		pass#TODO

	def readFuse(self):
		fuses = ""
		self.__enterPM()
		self.progressMeterInit("Reading fuses", 0)
		self.__sendInstr(SDI=0x04, SII=0x4C)
		self.__sendInstr(SDI=0x00, SII=0x68)
		self.__sendInstr(SDI=0x00, SII=0x6C)
		data = self.__getSDOBuffer()
		data = (data >> 3) & 0xFF
		fuses += chr(data)
		self.__sendInstr(SDI=0x04, SII=0x4C)
		self.__sendInstr(SDI=0x00, SII=0x7A)
		self.__sendInstr(SDI=0x00, SII=0x7E)
		data = self.__getSDOBuffer()
		data = ((data >> 3) & 0x1F) | 0xE0
		fuses += chr(data)
		self.progressMeterFinish()
		return fuses

	def writeFuse(self, image):
		if len(image) != 2:
			self.throwError("Invalid Fuses image size %d (expected %d)" %\
				(len(image), 2))
		self.__enterPM()
		self.progressMeterInit("Writing fuses", 0)
		self.__sendInstr(SDI=0x40, SII=0x4C)
		self.__sendInstr(SDI=ord(image[0]), SII=0x2C)
		self.__sendInstr(SDI=0x00, SII=0x64)
		self.__sendInstr(SDI=0x00, SII=0x6C)
		self.__waitHighSDO()
		self.__sendInstr(SDI=0x40, SII=0x4C)
		self.__sendInstr(SDI=(ord(image[1]) & 0x1F), SII=0x2C)
		self.__sendInstr(SDI=0x00, SII=0x74)
		self.__sendInstr(SDI=0x00, SII=0x7C)
		self.__waitHighSDO()
		self.progressMeterFinish()

	def readLockbits(self):
		pass#TODO

	def writeLockbits(self, image):
		pass#TODO

	def __readSignature(self):
		sig = ""
		self.__sendInstr(SDI=0x08, SII=0x4C)
		for i in range(0, 3):
			self.__sendInstr(SDI=i, SII=0x0C)
			self.__sendInstr(SDI=0x00, SII=0x68)
			self.__sendInstr(SDI=0x00, SII=0x6C)
			data = self.__getSDOBuffer()
			data = (data >> 3) & 0xFF
			sig += chr(data)
		return sig

	def __enterPM(self):
		"Enter HV programming mode."
		self.applyVCCX(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(12)
		self.applyGND(True)
		self.applyVCCX(True)

		self.__setPins(SCI=0, SDO_en=0, RST_en=1, RST=0)
		for i in range(0, 6):
			self.__setPins(SCI=0, SDO_en=0, RST_en=1, RST=0)
			self.__setPins(SCI=1, SDO_en=0, RST_en=1, RST=0)
		self.__setPins(SCI=0, SDO_en=1, SDO=0, RST_en=1, RST=0)
		self.top.delay(0.001)
		self.__setPins(SDO_en=1, SDO=0, RST_en=0)
		self.applyVPP(True)
		self.top.delay(0.001)
		self.__setPins(SDO_en=0)
		self.top.delay(0.01)

		signature = self.__readSignature()
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

	def __sendNOP(self):
		self.__sendInstr(SDI=0x00, SII=0x4C)

	def __sendInstr(self, SDI, SII):
		self.__setSDI(SDI)
		self.__setSII(SII)
		self.__runCommandSync(self.PROGCMD_SENDINSTR)

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
		self.top.cmdFPGAReadRaw(0x12)
		stat = self.top.cmdReadStatusReg()
		return ord(stat[0])

	def __getSDOBuffer(self):
		self.top.cmdFPGAReadRaw(0x13)
		self.top.cmdFPGAReadRaw(0x14)
		return self.top.cmdReadStatusReg16()

	def __rawSDOState(self):
		return bool(self.__getStatusFlags() & self.STAT_SDO)

	def __busy(self):
		return bool(self.__getStatusFlags() & self.STAT_BUSY)

	def __busyWait(self):
		for i in range(0, 100):
			if not self.__busy():
				return
			self.top.delay(0.01)
		self.throwError("Timeout in busywait.")

	def __waitHighSDO(self):
		for i in range(0, 100):
			if self.__rawSDOState():
				return
			self.top.delay(0.01)
		self.throwError("Timeout waiting for SDO.")

RegisteredChip(
	Chip_AtTiny13dip8,
	bitfile = "attiny13dip8",
	description = "Atmel AtTiny13",
	packages = ( ("DIP8", ""), ),
)
