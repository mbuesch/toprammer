"""
#    TOP2049 Open Source programming suite
#
#    28F102  Flash EEPROM
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

import math

class Chip_28fXXX_Dip40(Chip):
	"Generic 28f1024 Flash Memory (16-bit)"

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
	
	# The time in seconds between the erase and erase-verify (which stops the erase process)
	eraseDelay		= 0.010
	
	CMD_READ		= 0x00
	CMD_READ_SIG		= 0x90
	CMD_ERASE		= 0x20
	CMD_ERASE_VERIFY	= 0xA0
	CMD_PROGRAM		= 0x40
	CMD_PROGRAM_VERIFY	= 0xC0
	CMD_RESET		= 0xFF
	
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
	
	def erase(self):
		vppVolt = self.getChipOptionValue(
			"vpp_voltage",
			self.vppTable[self.chipType])
		writeZero = self.getChipOptionValue(
			"zero_before_erase", True)
		self.__eraseAlgo(vppVolt, self.ctype2size[self.chipType], writeZero)
	
	def __readimage(self, sizeBytes):
		"""Simple 8-bit data read algorithm."""
		self.progressMeterInit("Reading EEPROM", sizeBytes/2)
		image, count = [], 0
		self.__setFlags(oe=0, ce=0)
		self.addrSetter.reset()
		for addr in range(0, sizeBytes/2):
			self.progressMeter(addr)
			self.addrSetter.load(addr)
			self.__dataRead(False)
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
				"Got %d bytes, but EEPROM is only %d bytes." %\
				(len(image), sizeBytes))

		# Get the options
		vppVolt = self.getChipOptionValue(
			"vpp_voltage",
			self.vppTable[self.chipType])

		# Run the write algorithm
		self.__writeAlgo(image, vppVolt)

	def __writeAlgo(self, image, vppVolt):
		self.printInfo("Using %.2f VPP" % vppVolt)

		self.__turnOn()
		self.addrSetter.reset()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(vppVolt)
		# Program
		self.progressMeterInit("Writing EEPROM", len(image)/2)
		self.__setFlags(data_en=1, prog_en=1, ce=0, oe=1)
		self.applyVPP(True, [1])
		for addr in range(0, len(image)/2):
			self.progressMeter(addr)
			img_addr = addr*2
			data = byte2int(image[img_addr]) + (byte2int(image[img_addr+1]) << 8)
			self.__writeWord(addr, data)
			
		self.__dataWrite(self.CMD_READ)
		self.applyVPP(False)
		self.__setFlags()
		self.top.cmdSetVPPVoltage(5)

	def __writeWord(self, addr, data):
		self.addrSetter.load(addr)
		for retry in range(0, 25):
			self.__dataWrite(self.CMD_PROGRAM)
			self.__dataWrite(data)
			self.__dataWrite(self.CMD_PROGRAM_VERIFY)
			self.__setFlags(data_en=0, prog_en=0, ce=0, oe=0)
			readData = self.__dataRead(True)
			self.__setFlags(data_en=1, prog_en=1, ce=0, oe=1)
			if readData == data:
				break
		else:
			self.throwError("Failed to write EEPROM address %d" % addr)

	def __eraseAlgo(self, vppVolt, sizeBytes, writeZero):
		self.printInfo("Using %.2f VPP" % vppVolt)
		
		self.__turnOn()
		self.addrSetter.reset()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(vppVolt)
		self.__setFlags(data_en=1, prog_en=1, oe=1, ce=0)
		self.applyVPP(True, [1])
		
		# First overwrite everything with 0x0000
		if writeZero:
			self.printInfo("Overwrite chip with zero-data")
			self.progressMeterInit("Clearing data", sizeBytes/2)
			for addr in range(0, sizeBytes/2):
				self.progressMeter(addr)
				self.__writeWord(addr, 0)
		
		# Use the first non-zero address for the progress bar
		nonzero_address = 0
		self.printInfo("Erasing chip")
		self.progressMeterInit("Erasing chip", sizeBytes/2)
		# Execute Erase command
		for retry in range(0, 1000):
			self.__dataWrite(self.CMD_ERASE)
			self.__dataWrite(self.CMD_ERASE)
			self.top.hostDelay(self.eraseDelay)
			for addr in range(nonzero_address, sizeBytes/2):
				if not self.__eraseVerify(addr):
					break
				nonzero_address = addr
				self.progressMeter(addr)
			else:
				break
		else:
			self.throwError("Failed to erase EEPROM")
			
		self.__dataWrite(self.CMD_READ)
		self.applyVPP(False)
		self.__setFlags()
		self.top.cmdSetVPPVoltage(5)
		
	def __eraseVerify(self, addr):
		self.addrSetter.load(addr)
		self.__dataWrite(self.CMD_ERASE_VERIFY)
		self.__setFlags(data_en=0, prog_en=0, ce=0, oe=0)
		readData = self.__dataRead(True)
		self.__setFlags(data_en=1, prog_en=1, ce=0, oe=1)
		return readData == 0xFFFF

	def __readWord(self, addr):
		self.addrSetter.load(addr)
		return self.__dataRead(True)

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

	def __dataRead(self, returnData=False):
		self.top.cmdFPGARead(0)
		self.top.cmdFPGARead(1)
		if returnData:
			return self.top.cmdReadBufferReg16()
		
	def __dataWrite(self, data):
		self.__setDataPins(data)
		self.__progPulse(self.ppulseLengths[self.chipType])

	def __readSignature(self, vppVolt):
		self.addrSetter.reset()
		self.__turnOn()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(vppVolt)
		self.__setFlags(oe=0, ce=0)
		self.applyVPP(True, [31])
		for addr in xrange(2):
			self.addrSetter.load(addr)
			self.__dataRead(False)
		data = self.top.cmdReadBufferReg(4)
		manufacturer = data[1] + data[0]
		device = data[3] + data[2]
		self.applyVPP(False)
		self.__setFlags()
		self.top.cmdSetVPPVoltage(5)
		return manufacturer + device
		
		
class ChipDescription_28fXXX_Dip40(ChipDescription):
	"Generic 16-bit 28fXXX DIP40 ChipDescription"

	def __init__(self, chipImplClass, name):
		ChipDescription.__init__(self,
			chipImplClass = chipImplClass,
			bitfile = "_27cxxxdip40", # Use 27c1024 bitfile, it is compatible.
			chipID = name,
			runtimeID = (13, 1),
			chipType = ChipDescription.TYPE_EEPROM,
			chipVendors = "Various",
			description = name + " EEPROM",
			packages = ( ("DIP40", ""), ),
			chipOptions = (
				ChipOptionBool("zero_before_erase",
					"Write zero-data before erase operation"),
				ChipOptionFloat("vpp_voltage",
					"Override the default VPP voltage",
					minVal=10.0, maxVal=14.0),
			)
		)

class Chip_28f102(Chip_28fXXX_Dip40):
	def __init__(self):
		Chip_28fXXX_Dip40.__init__(self,
			chipType = Chip_28fXXX_Dip40.CTYPE_1024,
			chipPinVCC = 40,
			chipPinVPP = [1, 31],
			chipPinGND = 30)

ChipDescription_28fXXX_Dip40(Chip_28f102, "28f102")
