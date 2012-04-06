"""
#    TOP2049 Open Source programming suite
#
#    Generic SRAM chip
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


class Chip_genericSRAM(Chip):
	def __init__(self, chipPackage, chipPinVCC, chipPinGND,
		     VCCVoltage,
		     nrAddressBits, nrDataBits):
		Chip.__init__(self,
			      chipPackage = chipPackage,
			      chipPinVCC = chipPinVCC,
			      chipPinGND = chipPinGND)
		self.VCCVoltage = VCCVoltage
		self.nrAddressBits = nrAddressBits
		self.nrAddressBytes = int(math.ceil((float(self.nrAddressBits) - 0.1) / 8))
		self.nrDataBits = nrDataBits
		assert(nrDataBits == 8)

	def erase(self):
		self.writeRAM(int2byte(0) * self.__sizeBytes())

	def test(self):
		generic = GenericAlgorithms(self)
		generic.simpleTest(self.readRAM, self.writeRAM,
				   self.__sizeBytes())

	def readRAM(self):
		image = []

		self.progressMeterInit("Reading SRAM", self.__sizeBytes())
		self.__turnOnChip()
		self.__setControlPins(CE=0, OE=0, WE=1)
		nrBytes = 0
		for addr in range(0, self.__sizeBytes()):
			self.progressMeter(addr)
			self.__setAddress(addr)
			self.__readData()
			nrBytes += 1
			if nrBytes == self.top.getBufferRegSize():
				image.append(self.top.cmdReadBufferReg(nrBytes))
				nrBytes = 0
		image.append(self.top.cmdReadBufferReg(nrBytes))
		self.__setControlPins(CE=1, OE=1, WE=1)
		self.progressMeterFinish()

		return b"".join(image)

	def writeRAM(self, image):
		if len(image) > self.__sizeBytes():
			self.throwError("Invalid memory image size %d (expected max %d)" %\
				(len(image), self.__sizeBytes()))

		self.progressMeterInit("Writing SRAM", self.__sizeBytes())
		self.__turnOnChip()
		self.__setControlPins(CE=0, OE=1, WE=1)
		for addr in range(0, len(image)):
			self.progressMeter(addr)
			self.__setAddress(addr)
			self.__writeData(image[addr])
			self.__setControlPins(CE=0, OE=1, WE=0)
			self.top.cmdDelay(0.00000007) # Delay at least 70 nsec
			self.__setControlPins(CE=0, OE=1, WE=1)
		self.__setControlPins(CE=1, OE=1, WE=1)
		self.progressMeterFinish()

	def __sizeBytes(self):
		return (1 << self.nrAddressBits)

	def __turnOnChip(self):
		self.__setControlPins(CE=1, OE=1, WE=1)
		self.top.cmdSetVCCVoltage(self.VCCVoltage)
		self.applyGND(True)
		self.applyVCC(True)
		self.lastAddress = None

	def __setControlPins(self, CE=1, OE=1, WE=1):
		value = 0
		if CE:
			value |= 1
		if OE:
			value |= 2
		if WE:
			value |= 4
		self.top.cmdFPGAWrite(0x11, value)

	def __writeData(self, data):
		data = byte2int(data)
		self.top.cmdFPGAWrite(0x10, data)

	def __readData(self):
		self.top.cmdFPGARead(0x10)

	def __setAddress(self, addr):
		for i in range(0, self.nrAddressBytes):
			shift = 8 * i
			mask = 0xFF << shift
			if self.lastAddress is None or\
			   (self.lastAddress & mask) != (addr & mask):
				self.top.cmdFPGAWrite(0x12 + i,
						      (addr & mask) >> shift)
		self.lastAddress = addr
