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
		self.writeEEPROM("\xFF" * self.eepromSize)

	def readEEPROM(self):
		self.__chipTurnOn()

		image = ""
		count = 0
		prevAddr = None
		self.progressMeterInit("Reading EEPROM", self.eepromSize)
		begin = True
		for addr in range(0, self.eepromSize):
			self.progressMeter(addr)
#			if prevAddr is None or (prevAddr & 0xFF00) != (addr & 0xFF00):
			if 1:
				print("setAddr %X" % addr)#XXX
				self.__setAddressExtension(addr, writeMode=False)
				print("ADRWRDEVSEL")
				self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_WRITE,
					      read=False, do_start=True, do_stop=False)
				self.__expectACK()
				print("ADRWR")
				self.__runI2C(data=addr & 0xFF,
					      read=False, do_start=False, do_stop=False)
				self.__expectACK()
				print("DATADEVSEL")
				self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_READ,
					      read=False, do_start=True, do_stop=False)
				self.__expectACK()
				print("DATAREAD")
				self.__runI2C(read=True, do_start=False, do_stop=True)
				self.__expectNACK()
				begin = True
				prevAddr = addr
#			else:
#				if begin:
#					self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_WRITE,
#						      read=False, do_start=True, do_stop=False)
#					self.__expectACK()
#					self.__runI2C(data=addr & 0xFF,
#						      read=False, do_start=False, do_stop=False)
#					self.__expectACK()
#					self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_READ,
#						      read=False, do_start=True, do_stop=False)
#					self.__expectACK()
#					self.__runI2C(read=True, do_start=False, do_stop=False)
#					self.__expectACK()
#					begin = False
#				else:
#	#				self.__runI2C(data=self.I2C_BASE_ADDR | self.currentAddrExt | self.I2C_READ,
#	#					      read=False, do_start=True, do_stop=False)
#					self.__runI2C(read=True, do_start=False, do_stop=False)
#					self.__expectACK()
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
			if prevAddr is None or (prevAddr & 0xFFF0) != (addr & 0xFFF0):
				self.__setAddressExtension(addr, writeMode=True)
				self.__runCommand(self.CMD_DEVSEL_WRITE, busyWait=True)
				self.__runCommand(self.CMD_SETADDR, busyWait=True)
				self.__setData(byte2int(image[addr]))
				self.__runCommand(self.CMD_DATA_WRITE, busyWait=True)
				prevAddr = addr
			else:
				self.__setData(byte2int(image[addr]))
				if (addr & 0xF) == 0xF:
					self.__runCommand(self.CMD_DATA_WRITE_STOP, busyWait=True)
				else:
					self.__runCommand(self.CMD_DATA_WRITE, busyWait=True)
		self.progressMeterFinish()

	def __readData(self):
		self.top.cmdFPGARead(0)

	def __setData(self, dataByte):
		self.top.cmdFPGAWrite(1, dataByte & 0xFF)

	def __setAddressExtension(self, address, writeMode):
		sizeMask = self.eepromSize - 1
		assert(sizeMask & ~0x7FF == 0)
		addrExt = address & 0x700 & sizeMask
		if self.currentAddrExt != addrExt or\
		   self.currentWriteMode != writeMode:
			self.currentAddrExt = addrExt
			self.currentWriteMode = writeMode
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

	def __runI2C(self, data=None, read=False, do_start=False, do_stop=False):
		if data is not None:
			self.__setData(data)
		else:
			self.__setData(0)
		command = (0x01 if read else 0) |\
			  (0x02 if do_start else 0) |\
			  (0x04 if do_stop else 0)
		self.top.cmdFPGAWrite(0, command)
		self.__busyWait()

	def __isBusy(self):
		(busy0, busy1, ack) = self.__getStatusFlags()
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
		ack = not bool(stat & 0x04)
		self.lastAck = ack
		return (busy0, busy1, ack)

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
	def __init__(self, chipImplClass, chipID, description, broken=False):
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
			broken = broken,
		)

ChipDescription_m24cXX(
	Chip_m24c01dip8,
	chipID = "m24c01dip8",
	description = "M24C01 I2C EEPROM",
	broken = True,
)

ChipDescription_m24cXX(
	Chip_m24c02dip8,
	chipID = "m24c02dip8",
	description = "M24C02 I2C EEPROM",
	broken = True,
)

ChipDescription_m24cXX(
	Chip_m24c04dip8,
	chipID = "m24c04dip8",
	description = "M24C04 I2C EEPROM",
	broken = True,
)

ChipDescription_m24cXX(
	Chip_m24c08dip8,
	chipID = "m24c08dip8",
	description = "M24C08 I2C EEPROM",
	broken = True,
)

ChipDescription_m24cXX(
	Chip_m24c16dip8,
	chipID = "m24c16dip8",
	description = "M24C16 I2C EEPROM",
	broken = True,
)
