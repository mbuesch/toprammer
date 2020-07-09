"""
#    TOP2049 Open Source programming suite
#
#    M24C16 I2C based serial EEPROM
#
#    Copyright (c) 2011-2017 Michael Buesch <m@bues.ch>
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
	I2C_BASE_ADDR	= 0x50 << 1
	I2C_READ	= 0x01
	I2C_WRITE	= 0x00

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
		self.currentWriteMode = None

	def erase(self):
		self.writeEEPROM(b"\xFF" * self.eepromSize)

	def readEEPROM(self):
		self.__chipTurnOn()

		image = b""
		prevAddr = None
		self.progressMeterInit("Reading EEPROM", self.eepromSize)
		for addr in range(0, self.eepromSize):
			self.progressMeter(addr)
			if prevAddr is None or (prevAddr & 0xFF00) != (addr & 0xFF00):
				self.__setAddressExtension(addr, writeMode=False)
				# Begin sequential random read
				self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_WRITE,
					      read=False, do_start=True, do_stop=False)
				self.__expectACK()
				self.__runI2C(data=addr & 0xFF,
					      read=False, do_start=False, do_stop=False)
				self.__expectACK()
				self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_READ,
					      read=False, do_start=True, do_stop=False)
				self.__expectACK()
				prevAddr = addr
			# Sequential random read
			if addr >= self.eepromSize - 1:
				# Last byte
				self.__runI2C(read=True, do_start=False, do_stop=True)
				self.__expectNACK()
			else:
				self.__runI2C(read=True, do_start=False, do_stop=False,
					      drive_ack=True)
				self.__expectACK()
			self.__readData()
			image += self.top.cmdReadBufferReg(1)
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
			if prevAddr is None or (prevAddr & 0xFFF0) != (addr & 0xFFF0):
				self.__setAddressExtension(addr, writeMode=True)
				self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_WRITE,
					      read=False, do_start=True, do_stop=False)
				self.__expectACK()
				self.__runI2C(data=addr & 0xFF,
					      read=False, do_start=False, do_stop=False)
				self.__expectACK()
				prevAddr = addr
			if (addr & 0xF) == 0xF:
				self.__runI2C(data=byte2int(image[addr]),
					      read=False, do_start=False, do_stop=True)
				self.__expectACK()
				self.top.cmdDelay(0.005) # Max write time
			else:
				self.__runI2C(data=byte2int(image[addr]),
					      read=False, do_start=False, do_stop=False)
				self.__expectACK()

		self.progressMeterFinish()

	def __readData(self):
		self.top.cmdFPGARead(0)

	def __setData(self, dataByte):
		self.top.cmdFPGAWrite(1, dataByte & 0xFF)

	def __setAddressExtension(self, address, writeMode):
		sizeMask = self.eepromSize - 1
		assert(sizeMask & ~0x7FF == 0)
		addrExt = ((address & 0x700 & sizeMask) >> 8) << 1

		if self.currentWriteMode != writeMode:
			E0 = E1 = E2 = 0
			E0_en = not (sizeMask & 0x0100)
			E1_en = not (sizeMask & 0x0200)
			E2_en = not (sizeMask & 0x0400)
			WC = not writeMode
			self.__setControlPins(E0=E0, E0_en=E0_en,
					      E1=E1, E1_en=E1_en,
					      E2=E2, E2_en=E2_en,
					      WC=WC)
		self.currentAddrExt = addrExt
		self.currentWriteMode = writeMode

	def __runI2C(self, data=None, read=False, do_start=False, do_stop=False, drive_ack=False):
		if data is not None:
			self.__setData(data)
		else:
			self.__setData(0)
		command = (0x01 if read else 0) |\
			  (0x02 if do_start else 0) |\
			  (0x04 if do_stop else 0) |\
			  (0x08 if drive_ack else 0)
		self.top.cmdFPGAWrite(0, command)
		self.__busyWait()

	def __isBusy(self):
		(busy, ack) = self.__getStatusFlags()
		return busy

	def __busyWait(self):
		for i in range(0, 100):
			if not self.__isBusy():
				return
			self.top.hostDelay(0.001)
		self.throwError("Timeout in busywait.")

	def __getStatusFlags(self):
		self.top.cmdFPGARead(1)
		stat = self.top.cmdReadBufferReg8()
		busy = bool(stat & 0x01)
		ack = not bool(stat & 0x02)
		self.lastAck = ack
		return (busy, ack)

	def __expectACK(self):
		if not self.lastAck:
			self.throwError("Expected I2C ACK, but received NACK")

	def __expectNACK(self):
		if self.lastAck:
			self.throwError("Expected I2C NACK, but received ACK")

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
		self.top.cmdFPGAWrite(2, value)

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
