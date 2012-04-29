"""
#    TOP2049 Open Source programming suite
#
#    M24C16 I2C based serial EEPROM
#
#    Copyright (c) 2011 Michael Buesch <m@bues.ch>
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


class Chip_m24cXXdip8_common(Chip):
	CMD_DEVSEL_READ		= 0
	CMD_DEVSEL_WRITE	= 1
	CMD_SETADDR		= 2
	CMD_DATA_READ		= 3
	CMD_DATA_READ_STOP	= 4
	CMD_DATA_WRITE		= 5
	CMD_DATA_WRITE_STOP	= 6

	def __init__(self, eepromSize):
		Chip.__init__(self,
			      chipPackage = "DIP8",
			      chipPinVCC = 8,
			      chipPinGND = 4)
		self.eepromSize = eepromSize	# in bytes

	def __chipTurnOn(self):
		self.top.cmdSetVCCVoltage(5)
		self.top.cmdSetVPPVoltage(5)
		self.applyVCC(True)
		self.applyVPP(False)
		self.applyGND(True)
		self.top.cmdEnableZifPullups(True)

		self.currentAddrExt = None

	def erase(self):
		self.writeEEPROM("\xFF" * self.eepromSize)

	def readEEPROM(self):
		self.__chipTurnOn()

		image = ""
		count = 0
		prevAddr = None
		self.progressMeterInit("Reading EEPROM", self.eepromSize)
		for addr in range(0, self.eepromSize):
			self.progressMeter(addr)
			if prevAddr is None or (prevAddr & 0xFF00) != (addr & 0xFF00):
				self.__setAddress(addr, writeMode=False)
				self.__runCommand(self.CMD_DEVSEL_WRITE)
				self.__runCommand(self.CMD_SETADDR)
				self.__runCommand(self.CMD_DEVSEL_READ)
				self.__runCommand(self.CMD_DATA_READ_STOP)
				prevAddr = addr
			else:
				self.__runCommand(self.CMD_DEVSEL_READ)
				self.__runCommand(self.CMD_DATA_READ_STOP)
			self.__readData()
			count += 1
			if count == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(count)
				count = 0
		image += self.top.cmdReadBufferReg(count)
		self.progressMeterFinish()

		return image

	def writeEEPROM(self, image):
		if len(image) > self.eepromSize:
			self.throwError("Invalid EEPROM image size %d (expected <=%d)" %\
				(len(image), self.eepromSize))
		self.__chipTurnOn()

		self.progressMeterInit("Writing EEPROM", len(image))
		prevAddr = None
		for addr in range(0, len(image)):
			self.progressMeter(addr)
			self.__setData(byte2int(image[addr]))
			if prevAddr is None or (prevAddr & 0xFFF0) != (addr & 0xFFF0):
				self.__setAddress(addr, writeMode=True)
				self.__runCommand(self.CMD_DEVSEL_WRITE, busyWait=True)
				self.__runCommand(self.CMD_SETADDR, busyWait=True)
				self.__runCommand(self.CMD_DATA_WRITE, busyWait=True)
				prevAddr = addr
			else:
				if (addr & 0xF) == 0xF:
					self.__runCommand(self.CMD_DATA_WRITE_STOP, busyWait=True)
				else:
					self.__runCommand(self.CMD_DATA_WRITE, busyWait=True)
		self.progressMeterFinish()

	def __readData(self):
		self.top.cmdFPGARead(0)

	def __setData(self, dataByte):
		self.top.cmdFPGAWrite(2, dataByte & 0xFF)

	def __setAddress(self, address, writeMode):
		# Address base
		self.top.cmdFPGAWrite(1, address & 0xFF)
		# Address extension
		sizeMask = self.eepromSize - 1
		assert(sizeMask & ~0x7FF == 0)
		addrExt = address & 0x700 & sizeMask
		if self.currentAddrExt != addrExt:
			self.currentAddrExt = addrExt
			if sizeMask & 0x0100:
				E0 = addrExt & 0x0100
				E0_en = 0
			else:
				E0 = 0
				E0_en = 1
			if sizeMask & 0x0200:
				E1 = addrExt & 0x0200
				E1_en = 0
			else:
				E1 = 0
				E1_en = 1
			if sizeMask & 0x0400:
				E2 = addrExt & 0x0400
				E2_en = 0
			else:
				E2 = 0
				E2_en = 1
			if writeMode:
				WC = 0
			else:
				WC = 1
			self.__setControlPins(E0=E0, E0_en=E0_en,
					      E1=E1, E1_en=E1_en,
					      E2=E2, E2_en=E2_en,
					      WC=WC)

	def __runCommand(self, command, busyWait=False):
		self.top.cmdFPGAWrite(0, command & 0xFF)
		if busyWait:
			self.__busyWait()
		else:
			# We do not read busy flags, but wait long enough for
			# the operation to finish. This is safe for eeprom read.
			self.top.cmdDelay(0.00009)

	def __isBusy(self):
		(busy0, busy1) = self.__getStatusFlags()
		return busy0 != busy1

	def __busyWait(self):
		for i in range(0, 100):
			if not self.__isBusy():
				return
			self.top.hostDelay(0.001)
		self.throwError("Timeout in busywait.")

	def __getStatusFlags(self):
		self.top.cmdFPGARead(1)
		stat = self.top.cmdReadBufferReg8()
		busy0 = bool(stat & 0x01)
		busy1 = bool(stat & 0x02)
		return (busy0, busy1)

	def __setControlPins(self, E0, E0_en, E1, E1_en, E2, E2_en, WC):
		value = 0
		if E0:
			value |= (1 << 0)
		if E0_en:
			value |= (1 << 1)
		if E1:
			value |= (1 << 2)
		if E1_en:
			value |= (1 << 3)
		if E2:
			value |= (1 << 4)
		if E2_en:
			value |= (1 << 5)
		if WC:
			value |= (1 << 6)
		self.top.cmdFPGAWrite(3, value)

class Chip_m24c01dip8(Chip_m24cXXdip8_common):
	def __init__(self):
		Chip_m24cXXdip8_common.__init__(self, eepromSize = 1024 * 1 // 8)

class Chip_m24c02dip8(Chip_m24cXXdip8_common):
	def __init__(self):
		Chip_m24cXXdip8_common.__init__(self, eepromSize = 1024 * 2 // 8)

class Chip_m24c04dip8(Chip_m24cXXdip8_common):
	def __init__(self):
		Chip_m24cXXdip8_common.__init__(self, eepromSize = 1024 * 4 // 8)

class Chip_m24c08dip8(Chip_m24cXXdip8_common):
	def __init__(self):
		Chip_m24cXXdip8_common.__init__(self, eepromSize = 1024 * 8 // 8)

class Chip_m24c16dip8(Chip_m24cXXdip8_common):
	def __init__(self):
		Chip_m24cXXdip8_common.__init__(self, eepromSize = 1024 * 16 // 8)

class ChipDescription_m24cXX(ChipDescription):
	def __init__(self, chipImplClass, chipID, description):
		ChipDescription.__init__(self,
			chipImplClass = chipImplClass,
			bitfile = "m24c16dip8",
			chipID = chipID,
			runtimeID = (0x000B, 0x01),
			chipType = ChipDescription.TYPE_EEPROM,
			chipVendors = "ST",
			description = description,
			packages = (
				("DIP8", ""),
				("SO8", "With 1:1 adapter"),
				("TSSOP8", "With 1:1 adapter"),
			),
		)

ChipDescription_m24cXX(
	Chip_m24c01dip8,
	chipID = "m24c01dip8",
	description = "M24C01 I2C EEPROM",
)

ChipDescription_m24cXX(
	Chip_m24c02dip8,
	chipID = "m24c02dip8",
	description = "M24C02 I2C EEPROM",
)

ChipDescription_m24cXX(
	Chip_m24c04dip8,
	chipID = "m24c04dip8",
	description = "M24C04 I2C EEPROM",
)

ChipDescription_m24cXX(
	Chip_m24c08dip8,
	chipID = "m24c08dip8",
	description = "M24C08 I2C EEPROM",
)

ChipDescription_m24cXX(
	Chip_m24c16dip8,
	chipID = "m24c16dip8",
	description = "M24C16 I2C EEPROM",
)
