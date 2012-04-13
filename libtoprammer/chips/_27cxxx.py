"""
#    TOP2049 Open Source programming suite
#
#    27c16dip28  UV/OTP EPROM
#    27c32dip28  UV/OTP EPROM
#    27c64dip28  UV/OTP EPROM
#    27c128dip28 UV/OTP EPROM
#    27c256dip28 UV/OTP EPROM
#    27c512dip28 UV/OTP EPROM
#    Various manufacturers
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

from libtoprammer.chip import *
from libtoprammer.util import *


class Chip_27cXXX(Chip):
	"Generic 27cXXX EPROM"

	CTYPE_16	= 0
	CTYPE_32	= 1
	CTYPE_64	= 2
	CTYPE_128	= 3
	CTYPE_256	= 4
	CTYPE_512	= 5

	# Type to size (in bytes)
	ctype2size = {
		CTYPE_16	: 16 * 1024 // 8,
		CTYPE_32	: 32 * 1024 // 8,
		CTYPE_64	: 64 * 1024 // 8,
		CTYPE_128	: 128 * 1024 // 8,
		CTYPE_256	: 256 * 1024 // 8,
		CTYPE_512	: 512 * 1024 // 8,
	}

	def __init__(self, chipType,
		     chipPinVCC, chipPinVPP, chipPinGND):
		Chip.__init__(self, chipPackage = "DIP28",
			      chipPinVCC = chipPinVCC,
			      chipPinsVPP = chipPinVPP,
			      chipPinGND = chipPinGND)
		self.chipType = chipType
		self.generic = GenericAlgorithms(self)
		self.addrSetter = AddrSetter(self, 0, 1)

	def readEEPROM(self):
		self.__turnOn()
		return self.generic.simpleReadEPROM(
			sizeBytes = self.ctype2size[self.chipType],
			readData8Func = self.__dataRead,
			addrSetter = self.addrSetter,
			initFunc = lambda: self.__setFlags(oe=0, ce=0),
			exitFunc = lambda: self.__setFlags(oe=1, ce=1)
		)

#	def writeEEPROM(self):
#		pass#TODO

	def __turnOn(self):
		self.__setType(self.chipType)
		self.__setFlags()
		self.generic.simpleVoltageSetup()

	def __setDataPins(self, value):
		self.top.cmdFPGAWrite(2, value)

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
		self.top.cmdFPGAWrite(3, value)

	def __progPulse(self, usec):
		value = roundup(usec, 100) // 100
		if value > 0x7F:
			value = roundup(value, 8) // 8
			if value > 0x7F:
				self.throwError("__progPulse time too big")
			value |= 0x80 # Set "times 8" multiplier
		self.top.cmdFPGAWrite(4, value)

	def __setType(self, typeNumber):
		self.top.cmdFPGAWrite(5, typeNumber)

	def __dataRead(self):
		self.top.cmdFPGARead(0)

class Chip_27c16(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_16,
			chipPinVCC = 26,
			chipPinVPP = 23,
			chipPinGND = 14)

ChipDescription(Chip_27c16,
	bitfile = "_27cxxxdip28",
	chipID = "27c16",
	runtimeID = (12, 1),
	chipType = ChipDescription.TYPE_EPROM,
	chipVendors = "Various",
	description = "27c16 EPROM",
	packages = ( ("DIP28", ""), )
)

class Chip_27c32(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_32,
			chipPinVCC = 26,
			chipPinVPP = 22,
			chipPinGND = 14)

ChipDescription(Chip_27c32,
	bitfile = "_27cxxxdip28",
	chipID = "27c32",
	runtimeID = (12, 1),
	chipType = ChipDescription.TYPE_EPROM,
	chipVendors = "Various",
	description = "27c32 EPROM",
	packages = ( ("DIP28", ""), )
)

class Chip_27c64(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_64,
			chipPinVCC = 28,
			chipPinVPP = 1,
			chipPinGND = 14)

ChipDescription(Chip_27c64,
	bitfile = "_27cxxxdip28",
	chipID = "27c64",
	runtimeID = (12, 1),
	chipType = ChipDescription.TYPE_EPROM,
	chipVendors = "Various",
	description = "27c64 EPROM",
	packages = ( ("DIP28", ""), )
)

class Chip_27c128(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_128,
			chipPinVCC = 28,
			chipPinVPP = 1,
			chipPinGND = 14)

ChipDescription(Chip_27c128,
	bitfile = "_27cxxxdip28",
	chipID = "27c128",
	runtimeID = (12, 1),
	chipType = ChipDescription.TYPE_EPROM,
	chipVendors = "Various",
	description = "27c128 EPROM",
	packages = ( ("DIP28", ""), )
)

class Chip_27c256(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_256,
			chipPinVCC = 28,
			chipPinVPP = 1,
			chipPinGND = 14)

ChipDescription(Chip_27c256,
	bitfile = "_27cxxxdip28",
	chipID = "27c256",
	runtimeID = (12, 1),
	chipType = ChipDescription.TYPE_EPROM,
	chipVendors = "Various",
	description = "27c256 EPROM",
	packages = ( ("DIP28", ""), )
)

class Chip_27c512(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_512,
			chipPinVCC = 28,
			chipPinVPP = 22,
			chipPinGND = 14)

ChipDescription(Chip_27c512,
	bitfile = "_27cxxxdip28",
	chipID = "27c512",
	runtimeID = (12, 1),
	chipType = ChipDescription.TYPE_EPROM,
	chipVendors = "Various",
	description = "27c512 EPROM",
	packages = ( ("DIP28", ""), )
)
