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

	# Chip sizes (in bytes)
	ctype2size = {
		CTYPE_16	: 16 * 1024 // 8,
		CTYPE_32	: 32 * 1024 // 8,
		CTYPE_64	: 64 * 1024 // 8,
		CTYPE_128	: 128 * 1024 // 8,
		CTYPE_256	: 256 * 1024 // 8,
		CTYPE_512	: 512 * 1024 // 8,
	}

	# Programming voltages
	vppTable = {
		CTYPE_16	: 12.75,
		CTYPE_32	: 12.75,
		CTYPE_64	: 12.75,
		CTYPE_128	: 12.75,
		CTYPE_256	: 12.75,
		CTYPE_512	: 12.75,
	}

	# Programming pulse lengths (in microseconds)
	ppulseLengths = {
		CTYPE_16	: 1000,
		CTYPE_32	: 1000,
		CTYPE_64	: 1000,
		CTYPE_128	: 1000,
		CTYPE_256	: 500,
		CTYPE_512	: 500,
	}

	# Can we read the chip with VPP enabled?
	readWithVPP = {
		CTYPE_16	: True,
		CTYPE_32	: False, # VPP is shared with OE
		CTYPE_64	: True,
		CTYPE_128	: True,
		CTYPE_256	: True,
		CTYPE_512	: False, # VPP is shared with OE
	}

	# Chips that need overprogramming pulse.
	# This may not be true for all manufacturers.
	# Let the user set the chip option 'overprogram_pulse' in that case.
	needOverprogram = {
		CTYPE_16	: True,
		CTYPE_32	: True,
		CTYPE_64	: True,
		CTYPE_128	: True,
		CTYPE_256	: True,
		CTYPE_512	: False,
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

	def writeEEPROM(self, image):
		sizeBytes = self.ctype2size[self.chipType]
		if len(image) > sizeBytes:
			self.throwError("Invalid image size. "
				"Got %d bytes, but EPROM is only %d bytes." %\
				(len(image), sizeBytes))

		# Get the options
		immediateVerify = self.getChipOptionValue(
			"immediate_verify",
			self.readWithVPP[self.chipType])
		overprogram = self.getChipOptionValue(
			"overprogram_pulse",
			self.needOverprogram[self.chipType])
		vppVolt = self.getChipOptionValue(
			"vpp_voltage",
			self.vppTable[self.chipType])
		progpulseUsec = self.getChipOptionValue(
			"ppulse_length",
			self.ppulseLengths[self.chipType])

		# Run the write algorithm
		self.__writeAlgo(image, vppVolt, immediateVerify, overprogram,
				 progpulseUsec)

	def __writeAlgo(self, image, vppVolt, immediateVerify, overprogramPulse,
			progpulseUsec):
		self.printInfo("Using %.2f VPP" % vppVolt)
		self.printInfo("Using %s verify." %\
			("immediate" if immediateVerify else "detached"))
		if immediateVerify and not self.readWithVPP[self.chipType]:
			self.printWarning("Immediate verify will be slow "
				"on this chip!")
		self.printInfo("%s overprogramming pulse." %\
			("Using" if overprogramPulse else "Not using"))
		if not immediateVerify and overprogramPulse:
			self.printWarning("Using overprogramming, but no "
				"immediate verify. This probably is NOT what "
				"you intended.")
		self.printInfo("Using ppulse length: %d microseconds" %\
			progpulseUsec)

		self.__turnOn()
		self.addrSetter.reset()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(vppVolt)
		okMask = [ False ] * len(image)
		nrRetries = 25
		for retry in range(0, nrRetries):
			# Program
			self.progressMeterInit("Writing EPROM", len(image))
			self.__setFlags(data_en=1, prog_en=1, ce=0, oe=1)
			self.applyVPP(True)
			for addr in range(0, len(image)):
				self.progressMeter(addr)
				if okMask[addr]:
					continue
				data = byte2int(image[addr])
				if data == 0xFF:
					okMask[addr] = True
				else:
					self.__writeByte(addr, data,
						immediateVerify, overprogramPulse,
						progpulseUsec)
			self.applyVPP(False)
			self.__setFlags(data_en=0, prog_en=0, ce=0, oe=0)
			self.progressMeterFinish()
			if immediateVerify:
				break
			if all(okMask):
				break
			# Detached verify
			readImage = self.generic.simpleReadEPROM(
				sizeBytes = len(image),
				readData8Func = self.__dataRead,
				addrSetter = self.addrSetter,
				initFunc = lambda: self.__setFlags(oe=0, ce=0),
				exitFunc = lambda: self.__setFlags(oe=1, ce=1)
			)
			for addr in range(0, len(image)):
				if okMask[addr]:
					continue
				if image[addr] == readImage[addr]:
					okMask[addr] = True
			if all(okMask):
				break
			self.printInfo("%d of %d bytes failed verification. "
				"Retrying those bytes..." %\
				(len([ ok for ok in okMask if ok]),
				 len(okMask)))
		else:
			self.throwError("Failed to write EPROM. "
				"Tried %d times." % nrRetries)
		self.__setFlags()
		self.top.cmdSetVPPVoltage(5)

	def __writeByte(self, addr, data,
			doVerify, doOverprogram, progpulseUsec):
		self.addrSetter.load(addr)
		self.__setDataPins(data)
		for retry in range(0, 25):
			self.__progPulse(progpulseUsec)
			if not doVerify:
				break
			# Immediate verify
			if not self.readWithVPP[self.chipType]:
				self.applyVPP(False)
			self.__setFlags(data_en=0, prog_en=0, ce=0, oe=0)
			readData = self.__readByte(addr)
			self.__setFlags(data_en=1, prog_en=1, ce=0, oe=1)
			if not self.readWithVPP[self.chipType]:
				self.applyVPP(True)
			if readData == data:
				break
		else:
			self.throwError("Failed to write EPROM address %d" % addr)
		if doOverprogram:
			self.addrSetter.load(addr)
			self.__progPulse(progpulseUsec * 3 * (retry + 1))

	def __readByte(self, addr):
		self.addrSetter.load(addr)
		self.__dataRead()
		return self.top.cmdReadBufferReg8()

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
		seconds = float(value & 0x7F) / 10000
		if value & 0x80:
			seconds *= 8
		self.top.cmdDelay(seconds)
		self.top.flushCommands()

	def __setType(self, typeNumber):
		self.top.cmdFPGAWrite(5, typeNumber)

	def __dataRead(self):
		self.top.cmdFPGARead(0)

class ChipDescription_27cXXX(ChipDescription):
	"Generic 27cXXX ChipDescription"

	def __init__(self, chipImplClass, name):
		ChipDescription.__init__(self,
			chipImplClass = chipImplClass,
			bitfile = "_27cxxxdip28",
			chipID = name,
			runtimeID = (12, 1),
			chipType = ChipDescription.TYPE_EPROM,
			chipVendors = "Various",
			description = name + " EPROM",
			packages = ( ("DIP28", ""), ),
			chipOptions = (
				ChipOptionBool("immediate_verify",
					"Immediately verify each written byte"),
				ChipOptionBool("overprogram_pulse",
					"Perform an 'overprogramming' pulse"),
				ChipOptionFloat("vpp_voltage",
					"Override the default VPP voltage",
					minVal=10.0, maxVal=14.0),
				ChipOptionInt("ppulse_length",
					"Force 'Programming pulse' length, in microseconds.",
					minVal=100, maxVal=10000),
			)
		)

class Chip_27c16(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_16,
			chipPinVCC = 26,
			chipPinVPP = 23,
			chipPinGND = 14)

ChipDescription_27cXXX(Chip_27c16, "27c16")

class Chip_27c32(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_32,
			chipPinVCC = 26,
			chipPinVPP = 22,
			chipPinGND = 14)

ChipDescription_27cXXX(Chip_27c32, "27c32")

class Chip_27c64(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_64,
			chipPinVCC = 28,
			chipPinVPP = 1,
			chipPinGND = 14)

ChipDescription_27cXXX(Chip_27c64, "27c64")

class Chip_27c128(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_128,
			chipPinVCC = 28,
			chipPinVPP = 1,
			chipPinGND = 14)

ChipDescription_27cXXX(Chip_27c128, "27c128")

class Chip_27c256(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_256,
			chipPinVCC = 28,
			chipPinVPP = 1,
			chipPinGND = 14)

ChipDescription_27cXXX(Chip_27c256, "27c256")

class Chip_27c512(Chip_27cXXX):
	def __init__(self):
		Chip_27cXXX.__init__(self,
			chipType = Chip_27cXXX.CTYPE_512,
			chipPinVCC = 28,
			chipPinVPP = 22,
			chipPinGND = 14)

ChipDescription_27cXXX(Chip_27c512, "27c512")
