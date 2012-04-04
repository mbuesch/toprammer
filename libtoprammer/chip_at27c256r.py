"""
#    TOP2049 Open Source programming suite
#
#    Atmel AT27C256R EPROM
#
#    Copyright (c) 2012 Michael Buesch <m@bues.ch>
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

class Chip_at27c256r(Chip):
	def __init__(self):
		Chip.__init__(self,
			      chipPackage = "DIP28",
			      chipPinVCCX = 28,
			      chipPinsVPP = 1,
			      chipPinGND = 14)
		self.sizeBytes = 32 * 1024

	def readEEPROM(self):
		self.__turnOn()
		self.progressMeterInit("Reading EPROM", self.sizeBytes)
		image, prevAddr, count = b"", None, 0
		self.__setFlags(oe=0, ce=0)
		for addr in range(0, self.sizeBytes):
			self.progressMeter(addr)
			if prevAddr is None or\
			   (prevAddr & 0xFF) != (addr & 0xFF):
				self.__setAddrLow(addr & 0xFF)
			if prevAddr is None or\
			   ((prevAddr >> 8) & 0xFF) != ((addr >> 8) & 0xFF):
				self.__setAddrHigh((addr >> 8) & 0xFF)
			prevAddr = addr
			self.__dataRead()
			count += 1
			if count == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg()
				count = 0
		if count:
			image += self.top.cmdReadBufferReg()
		self.__setFlags(oe=1, ce=1)
		self.progressMeterFinish()
		return image

#	def writeEEPROM(self):
#		pass#TODO

	def __turnOn(self):
		self.__setFlags()
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(5)
		self.applyVCCX(True)
		self.applyVPP(False)
		self.applyGND(True)

	def __setAddrLow(self, value):
		self.top.cmdFPGAWrite(0x10, value)

	def __setAddrHigh(self, value):
		self.top.cmdFPGAWrite(0x11, value)

	def __setDataPins(self, value):
		self.top.cmdFPGAWrite(0x12, value)

	def __setFlags(self, data_en=0, prog_en=0, ce=1, oe=1):
		value = 0
		if data_en:
			value |= (1 << 0)
		if prog_en:
			value |= (1 << 1)
		if ce:
			value |= (1 << 2)
		if oe:
			value |= (1 << 3)
		self.top.cmdFPGAWrite(0x13, value)

	def __progPulse(self):
		self.top.cmdFPGAWrite(0x14, 0)

	def __dataRead(self):
		self.top.cmdFPGARead(0x10)

ChipDescription(Chip_at27c256r,
	bitfile = "at27c256r",
	runtimeID = (0x000C, 0x01),
	chipType = ChipDescription.TYPE_EPROM,
	chipVendors = "Atmel",
	description = "AT27C256R",
	packages = ( ("DIP28", ""), )
)
