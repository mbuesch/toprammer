"""
#    TOP2049 Open Source programming suite
#
#    27c16dip1024  UV/OTP EPROM
#
#    Copyright (c) 2012 Michael Buesch <m@bues.ch>
#    Copyright (c) 2016 Tom van Leeuwen <gpl@tomvanleeuwen.nl>
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


class Chip_27cXXX_Dip40(Chip):
	"Generic 27c1024 EPROM (16-bit)"

	CTYPE_1024	= 0

	# Chip sizes (in bytes)
	ctype2size = {
		CTYPE_1024	: 1024 * 1024 // 8,
	}

	# Programming voltages
	vppTable = {
		CTYPE_1024	: 12.75,
	}

	# Programming pulse lengths (in microseconds)
	ppulseLengths = {
		CTYPE_1024	: 100,
	}

	# Can we read the chip with VPP enabled?
	readWithVPP = {
		CTYPE_1024	: True,
	}

	# Chips that need overprogramming pulse.
	# This may not be true for all manufacturers.
	# Let the user set the chip option 'overprogram_pulse' in that case.
	needOverprogram = {
		CTYPE_1024	: False,
	}

	def __init__(self, chipType,
		     chipPinVCC, chipPinVPP, chipPinGND):
		Chip.__init__(self, chipPackage = "DIP40",
			      chipPinVCC = chipPinVCC,
			      chipPinsVPP = chipPinVPP,
			      chipPinGND = chipPinGND)
		self.chipType = chipType
		self.generic = GenericAlgorithms(self)
		self.addrSetter = AddrSetter(self, 0, 1)

	def readSignature(self):
		vppVolt = self.getChipOptionValue(
			"vpp_voltage",
			self.vppTable[self.chipType])
		return self.__readSignature(vppVolt)
		
	def readEEPROM(self):
		self.__turnOn()
		return self.__readimage(self.ctype2size[self.chipType])
	
	def __readimage(self, sizeBytes):
		"""Simple 8-bit data read algorithm."""
		self.progressMeterInit("Reading EEPROM", sizeBytes/2)
		image, count = [], 0
		self.__setFlags(oe=0, ce=0)
		self.addrSetter.reset()
		for addr in range(0, sizeBytes/2):
			self.progressMeter(addr)
			self.addrSetter.load(addr)
			self.__dataRead()
			count += 2
			if count == self.top.getBufferRegSize():
				image.append(self.top.cmdReadBufferReg())
				count = 0
		if count:
			image.append(self.top.cmdReadBufferReg()[:count])
		self.__setFlags(oe=1, ce=1)
		self.progressMeterFinish()
		return b"".join(image)

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
		vppVolt = self.getChipOptionValue(
			"vpp_voltage",
			self.vppTable[self.chipType])
		progpulseUsec = self.getChipOptionValue(
			"ppulse_length",
			self.ppulseLengths[self.chipType])

		# Run the write algorithm
		self.__writeAlgo(image, vppVolt, immediateVerify, progpulseUsec)

	def __writeAlgo(self, image, vppVolt, immediateVerify, progpulseUsec):
		self.printInfo("Using %.2f VPP" % vppVolt)
		self.printInfo("Using %s verify." %\
			("immediate" if immediateVerify else "detached"))
		if immediateVerify and not self.readWithVPP[self.chipType]:
			self.printWarning("Immediate verify will be slow "
				"on this chip!")
		self.printInfo("Using ppulse length: %d microseconds" %\
			progpulseUsec)

		self.__turnOn()
		self.addrSetter.reset()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(vppVolt)
		okMask = [ False ] * (len(image)/2)
		nrRetries = 25
		for retry in range(0, nrRetries):
			# Program
			self.progressMeterInit("Writing EPROM", len(image)/2)
			self.__setFlags(data_en=1, prog_en=1, ce=0, oe=1)
			self.applyVPP(True, [1])
			for addr in range(0, len(image)/2):
				self.progressMeter(addr)
				if okMask[addr]:
					continue
				img_addr = addr*2
				data = byte2int(image[img_addr]) + (byte2int(image[img_addr+1]) << 8)
				if data == 0xFFFF:
					okMask[addr] = True
				else:
					self.__writeWord(addr, data,
						immediateVerify, progpulseUsec)
			self.applyVPP(False)
			self.__setFlags(data_en=0, prog_en=0, ce=0, oe=0)
			self.progressMeterFinish()
			if immediateVerify:
				break
			if all(okMask):
				break
			# Detached verify
			readImage = self.readimage()
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

	def __writeWord(self, addr, data,
			doVerify, progpulseUsec):
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
			readData = self.__readWord(addr)
			self.__setFlags(data_en=1, prog_en=1, ce=0, oe=1)
			if not self.readWithVPP[self.chipType]:
				self.applyVPP(True, [1])
			if readData == data:
				break
		else:
			self.throwError("Failed to write EPROM address %d" % addr)

	def __readWord(self, addr):
		self.addrSetter.load(addr)
		self.__dataRead()
		return self.top.cmdReadBufferReg16()

	def __turnOn(self):
		self.__setType(self.chipType)
		self.__setFlags()
		self.generic.simpleVoltageSetup()

	def __setDataPins(self, value):
		self.top.cmdFPGAWrite(2, value & 0xFF)
		self.top.cmdFPGAWrite(3, value >> 8)

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
		self.top.cmdFPGAWrite(4, value)

	def __progPulse(self, usec):
		value = roundup(usec, 100) // 100
		if value > 0x7F:
			value = roundup(value, 8) // 8
			if value > 0x7F:
				self.throwError("__progPulse time too big")
			value |= 0x80 # Set "times 8" multiplier
		self.top.cmdFPGAWrite(5, value)
		seconds = float(value & 0x7F) / 10000
		if value & 0x80:
			seconds *= 8
		self.top.cmdDelay(seconds)
		self.top.flushCommands()

	def __setType(self, typeNumber):
		self.top.cmdFPGAWrite(6, typeNumber)

	def __dataRead(self):
		self.top.cmdFPGARead(0)
		self.top.cmdFPGARead(1)

	def __readSignature(self, vppVolt):
		self.addrSetter.reset()
		self.__turnOn()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(vppVolt)
		self.__setFlags(oe=0, ce=0)
		self.applyVPP(True, [31])
		for addr in xrange(2):
			self.addrSetter.load(addr)
			self.__dataRead()
		data = self.top.cmdReadBufferReg(4)
		manufacturer = data[1] + data[0]
		device = data[3] + data[2]
		self.applyVPP(False)
		self.__setFlags()
		self.top.cmdSetVPPVoltage(5)
		return manufacturer + device
		
		
class ChipDescription_27cXXX_Dip40(ChipDescription):
	"Generic 16-bit 27cXXX DIP40 ChipDescription"

	def __init__(self, chipImplClass, name):
		ChipDescription.__init__(self,
			chipImplClass = chipImplClass,
			bitfile = "_27cxxxdip40",
			chipID = name,
			runtimeID = (13, 1),
			chipType = ChipDescription.TYPE_EPROM,
			chipVendors = "Various",
			description = name + " EPROM",
			packages = ( ("DIP40", ""), ),
			chipOptions = (
				ChipOptionBool("immediate_verify",
					"Immediately verify each written byte"),
				ChipOptionFloat("vpp_voltage",
					"Override the default VPP voltage",
					minVal=10.0, maxVal=14.0),
				ChipOptionInt("ppulse_length",
					"Force 'Programming pulse' length, in microseconds.",
					minVal=100, maxVal=10000),
			)
		)

class Chip_27c1024(Chip_27cXXX_Dip40):
	def __init__(self):
		Chip_27cXXX_Dip40.__init__(self,
			chipType = Chip_27cXXX_Dip40.CTYPE_1024,
			chipPinVCC = 40,
			chipPinVPP = [1, 31],
			chipPinGND = 30)

ChipDescription_27cXXX_Dip40(Chip_27c1024, "27c1024")
