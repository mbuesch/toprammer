"""
#    TOP2049 Open Source programming suite
#
#    Winbond W29EE011 DIP32
#    Winbond W29EE011 PLCC32 (inside 1:1 PLCC32->DIP32 adapter)
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


class Chip_w29ee011dip32(Chip):
	PROGCMD_WRITEBUF	= 1 # Write buffer to chip

	STAT_BUSY		= 0x01 # Programmer is running a command

	def __init__(self):
		Chip.__init__(self,
			      chipPackage = "DIP32",
			      chipPinVCCX = 32,
			      chipPinsVPP = None,
			      chipPinGND = 16)

	def initializeChip(self):
		self.printDebug("Initializing chip")
		self.applyVCCX(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.top.queueCommand("\x0E\x28\x01\x00")
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

	def erase(self):
		self.applyVCCX(True)
		self.applyVPP(True)
		self.applyGND(True)

		commands = (
			(0x5555, 0xAA),
			(0x2AAA, 0x55),
			(0x5555, 0x80),
			(0x5555, 0xAA),
			(0x2AAA, 0x55),
			(0x5555, 0x10),
		)

		self.progressMeterInit("Erasing chip", 0)
		self.__resetBufferPointers()
		for command in commands:
			self.__appendJEDEC(command[0], command[1])
		self.__setCEOE(CE=0, OE=1)
		self.__runCommandSync(self.PROGCMD_WRITEBUF)
		self.top.delay(0.050)
		self.__setCEOE(CE=1, OE=1)
		self.progressMeterFinish()

	def readEEPROM(self):
		self.applyVCCX(True)
		self.applyVPP(True)
		self.applyGND(True)

		image = ""
		self.progressMeterInit("Reading EEPROM", 0x20000)
		self.__setCEOE(CE=0, OE=0)
		prevAddr = 0xFFFFFFFF
		byteCount = 0
		for addr in range(0, 0x20000):
			self.progressMeter(addr)
			if (addr & 0xFF) != (prevAddr & 0xFF):
				self.__loadReadAddrLo(addr)
			if (addr & 0xFF00) != (prevAddr & 0xFF00):
				self.__loadReadAddrMed(addr >> 8)
			if (addr & 0xFF0000) != (prevAddr & 0xFF0000):
				self.__loadReadAddrHi(addr >> 16)
			prevAddr = addr
			self.top.cmdFPGAReadByte()
			byteCount += 1
			if byteCount == 64:
				image += self.top.cmdReadStatusReg()
				byteCount = 0
		assert(byteCount == 0)
		self.__setCEOE(CE=1, OE=1)
		self.progressMeterFinish()

		return image

	def writeEEPROM(self, image):
		if len(image) > 0x20000:
			self.throwError("Invalid EPROM image size %d (expected <=%d)" %\
				(len(image), 0x20000))

		self.applyVCCX(True)
		self.applyVPP(True)
		self.applyGND(True)

		self.progressMeterInit("Writing EEPROM", len(image))
		self.__setCEOE(CE=0, OE=1)
		for addr in range(0, len(image), 128):
			self.progressMeter(addr)
			pagelen = min(128, len(image) - addr)
			page = image[addr:addr+pagelen]
			self.__writePage(addr, page)
		self.__setCEOE(CE=1, OE=1)
		self.progressMeterFinish()

	def __writePage(self, pageAddress, pageData):
		commands = (
			(0x5555, 0xAA),
			(0x2AAA, 0x55),
			(0x5555, 0xA0),
		)
		self.__resetBufferPointers()
		for command in commands:
			self.__appendJEDEC(command[0], command[1])
		assert(len(pageData) <= 128)
		for byte in pageData:
			self.__writeBufAppend(ord(byte))
		self.__loadWriteAddr(pageAddress)
		self.__runCommandSync(self.PROGCMD_WRITEBUF)
		self.top.delay(0.010)

	def __writeBufAppend(self, byte):
		# This also auto-increments the write buffer pointer
		self.top.cmdFPGAWrite(0x10, byte & 0xFF)

	def __resetBufferPointers(self):
		self.top.cmdFPGAWrite(0x13, 0)

	def __loadCommand(self, command):
		self.top.cmdFPGAWrite(0x12, command & 0xFF)

	def __runCommandSync(self, command):
		self.__loadCommand(command)
		self.__busyWait()

	def __loadWriteAddr(self, addr):
		self.__loadWriteAddrLo(addr)
		self.__loadWriteAddrMed(addr >> 8)
		self.__loadWriteAddrHi(addr >> 16)

	def __loadWriteAddrLo(self, addrLo):
		self.top.cmdFPGAWrite(0x14, addrLo & 0xFF)

	def __loadWriteAddrMed(self, addrMed):
		self.top.cmdFPGAWrite(0x15, addrMed & 0xFF)

	def __loadWriteAddrHi(self, addrHi):
		self.top.cmdFPGAWrite(0x16, addrHi & 0xFF)

	def __loadReadAddrLo(self, addrLo):
		self.top.cmdFPGAWrite(0x17, addrLo & 0xFF)

	def __loadReadAddrMed(self, addrMed):
		self.top.cmdFPGAWrite(0x18, addrMed & 0xFF)

	def __loadReadAddrHi(self, addrHi):
		self.top.cmdFPGAWrite(0x19, addrHi & 0xFF)

	def __setCEOE(self, CE, OE):
		data = 0
		if CE:
			data |= 0x01
		if OE:
			data |= 0x02
		self.top.cmdFPGAWrite(0x1A, data)

	def __appendJEDEC(self, addr, data):
		self.__loadJEDECAddrLo(addr)
		self.__loadJEDECAddrMed(addr >> 8)
		self.__loadJEDECAddrHi(addr >> 16)
		self.__loadJEDECData(data)

	def __loadJEDECAddrLo(self, addrLo):
		self.top.cmdFPGAWrite(0x1B, addrLo & 0xFF)

	def __loadJEDECAddrMed(self, addrMed):
		self.top.cmdFPGAWrite(0x1C, addrMed & 0xFF)

	def __loadJEDECAddrHi(self, addrHi):
		self.top.cmdFPGAWrite(0x1D, addrHi & 0xFF)

	def __loadJEDECData(self, data):
		# This also auto-increments the JEDEC buffer pointer
		self.top.cmdFPGAWrite(0x1E, data & 0xFF)

	def __getStatusFlags(self):
		self.top.cmdFPGAReadRaw(0x12)
		stat = self.top.cmdReadStatusReg()
		return ord(stat[0])

	def __busy(self):
		return bool(self.__getStatusFlags() & self.STAT_BUSY)

	def __busyWait(self):
		for i in range(0, 100):
			if not self.__busy():
				return
			self.top.delay(0.01)
		self.throwError("Timeout in busywait.")

RegisteredChip(
	Chip_w29ee011dip32,
	bitfile = "w29ee011dip32",
	description = "Winbond W29EE011 EEPROM",
	packages = ( ("DIP32", ""), ("PLCC32", "Use 1:1 PLCC32->DIP32 adapter"), )
)