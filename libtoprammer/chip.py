"""
#    TOP2049 Open Source programming suite
#
#    Chip support
#
#    Copyright (c) 2009-2011 Michael Buesch <mb@bu3sch.de>
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

from util import *
from layout_generator import *
from user_interface import *


class Chip:
	SUPPORT_ERASE		= (1 << 0)
	SUPPORT_SIGREAD		= (1 << 1)
	SUPPORT_PROGMEMREAD	= (1 << 2)
	SUPPORT_PROGMEMWRITE	= (1 << 3)
	SUPPORT_EEPROMREAD	= (1 << 4)
	SUPPORT_EEPROMWRITE	= (1 << 5)
	SUPPORT_FUSEREAD	= (1 << 6)
	SUPPORT_FUSEWRITE	= (1 << 7)
	SUPPORT_LOCKREAD	= (1 << 8)
	SUPPORT_LOCKWRITE	= (1 << 9)
	SUPPORT_RAMREAD		= (1 << 10)
	SUPPORT_RAMWRITE	= (1 << 11)
	SUPPORT_TEST		= (1 << 12)

	@staticmethod
	def chipSupportsAttr(chipImplClass, attribute):
		"""Check if a chip implementation supports a feature.
		'attribute' is the class member function to check for"""
		# This works by checking whether the subclass overloaded
		# the member function attribute.
		if str(type(chipImplClass)) == "<type 'instance'>":
			# This is an instance. Get the class
			chipImplClass = chipImplClass.registeredChip.chipImplClass
		return getattr(chipImplClass, attribute) != getattr(Chip, attribute)

	@staticmethod
	def getSupportFlags(chip):
		"Get the SUPPORT_... flags for this chip"
		flags = 0
		for (methodName, flag) in (
				("erase",		Chip.SUPPORT_ERASE),
				("readSignature",	Chip.SUPPORT_SIGREAD),
				("readProgmem",		Chip.SUPPORT_PROGMEMREAD),
				("writeProgmem",	Chip.SUPPORT_PROGMEMWRITE),
				("readEEPROM",		Chip.SUPPORT_EEPROMREAD),
				("writeEEPROM",		Chip.SUPPORT_EEPROMWRITE),
				("readFuse",		Chip.SUPPORT_FUSEREAD),
				("writeFuse",		Chip.SUPPORT_FUSEWRITE),
				("readLockbits",	Chip.SUPPORT_LOCKREAD),
				("writeLockbits",	Chip.SUPPORT_LOCKWRITE),
				("readRAM",		Chip.SUPPORT_RAMREAD),
				("writeRAM",		Chip.SUPPORT_RAMWRITE),
				("test",		Chip.SUPPORT_TEST)):
			if Chip.chipSupportsAttr(chip, methodName):
				flags |= flag
		return flags

	def __init__(self, chipPackage=None, chipPinVCCX=None, chipPinsVPP=None, chipPinGND=None):
		"""chipPackage is the ID string for the package.
		May be None, if no initial auto-layout is required.
		chipPinVCCX is the required VCCX pin on the package.
		chipPinVPP is the required VPP pin on the package.
		chipPinGND is the required GND pin on the package."""

		self.__chipPackage = chipPackage
		self.__chipPinVCCX = chipPinVCCX
		self.__chipPinsVPP = chipPinsVPP
		self.__chipPinGND = chipPinGND

	def setTOP(self, top):
		self.top = top

	def setChipID(self, chipID):
		self.chipID = chipID

	def setProgrammerType(self, programmerType):
		"Set the TOP programmer type. See class TOP.TYPE_..."
		self.programmerType = programmerType

	def printWarning(self, message):
		self.top.printWarning(self.chipID + ": " + message)

	def printInfo(self, message):
		self.top.printInfo(self.chipID + ": " + message)

	def printDebug(self, message):
		self.top.printDebug(self.chipID + ": " + message)

	def throwError(self, message):
		raise TOPException(self.chipID + ": " + message)

	def generateVoltageLayouts(self):
		if self.__chipPackage:
			self.generator = createLayoutGenerator(self.__chipPackage)
			self.generator.setProgrammerType(self.programmerType)
			self.generator.setPins(vccxPin=self.__chipPinVCCX,
					       vppPins=self.__chipPinsVPP,
					       gndPin=self.__chipPinGND)
			self.generator.recalculate()

	def getLayoutGenerator(self):
		if self.__chipPackage:
			return self.generator
		return None

	def applyVCCX(self, turnOn):
		"Turn VCCX on, using the auto-layout."
		if turnOn:
			try:
				generator = self.generator
			except (AttributeError), e:
				self.throwError("BUG: Using auto-layout, but did not initialize it.")
			generator.applyVCCXLayout(self.top)
		else:
			self.top.vccx.setLayoutMask(0)

	def applyVPP(self, turnOn, packagePinsToTurnOn=[]):
		"""Turn VPP on, using the auto-layout.
		packagePinsToTurnOn is a list of pins on the package to drive to VPP.
		If it is not passed (or an empty list), all VPP pins of the layout are turned on.
		The parameter is unused, if turnOn=False."""
		if turnOn:
			try:
				generator = self.generator
			except (AttributeError), e:
				self.throwError("BUG: Using auto-layout, but did not initialize it.")
			generator.applyVPPLayout(self.top, packagePinsToTurnOn)
		else:
			self.top.vpp.setLayoutMask(0)

	def applyGND(self, turnOn):
		"Turn GND on, using the auto-layout."
		if turnOn:
			try:
				generator = self.generator
			except (AttributeError), e:
				self.throwError("BUG: Using auto-layout, but did not initialize it.")
			generator.applyGNDLayout(self.top)
		else:
			self.top.gnd.setLayoutMask(0)

	def progressMeterInit(self, message, nrSteps):
		self.top.progressMeterInit(AbstractUserInterface.PROGRESSMETER_CHIPACCESS,
					   message, nrSteps)

	def progressMeterFinish(self):
		self.top.progressMeterFinish(AbstractUserInterface.PROGRESSMETER_CHIPACCESS)

	def progressMeter(self, step):
		self.top.progressMeter(AbstractUserInterface.PROGRESSMETER_CHIPACCESS,
				       step)

	def genericTest(self, readFunc, writeFunc, size):
		"Generic test. Call from test() in the chip implementation, if desired."
		image = genRandomBlob(size)
		writeFunc(image)
		if readFunc() != image:
			self.throwError("Unit-test failed. The chip may be physically broken.")

	def shutdownChip(self):
		# Override me in the subclass, if required.
		self.printDebug("Default chip shutdown")
		self.applyVCCX(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.top.cmdSetVCCXVoltage(self.top.vccx.minVoltage())
		self.top.cmdSetVPPVoltage(self.top.vpp.minVoltage())

	def readSignature(self):
		# Override me in the subclass, if required.
		raise TOPException("Signature reading not supported on " + self.chipID)

	def erase(self):
		# Override me in the subclass, if required.
		raise TOPException("Chip erasing not supported on " + self.chipID)

	def test(self):
		# Override me in the subclass, if required.
		raise TOPException("Chip testing not supported on " + self.chipID)

	def readProgmem(self):
		# Override me in the subclass, if required.
		raise TOPException("Program memory reading not supported on " + self.chipID)

	def writeProgmem(self, image):
		# Override me in the subclass, if required.
		raise TOPException("Program memory writing not supported on " + self.chipID)

	def readEEPROM(self):
		# Override me in the subclass, if required.
		raise TOPException("EEPROM reading not supported on " + self.chipID)

	def writeEEPROM(self, image):
		# Override me in the subclass, if required.
		raise TOPException("EEPROM writing not supported on " + self.chipID)

	def readFuse(self):
		# Override me in the subclass, if required.
		raise TOPException("Fuse reading not supported on " + self.chipID)

	def writeFuse(self, image):
		# Override me in the subclass, if required.
		raise TOPException("Fuse writing not supported on " + self.chipID)

	def readLockbits(self):
		# Override me in the subclass, if required.
		raise TOPException("Lockbit reading not supported on " + self.chipID)

	def writeLockbits(self, image):
		# Override me in the subclass, if required.
		raise TOPException("Lockbit writing not supported on " + self.chipID)

	def readRAM(self):
		# Override me in the subclass, if required.
		raise TOPException("RAM reading not supported on " + self.chipID)

	def writeRAM(self, image):
		# Override me in the subclass, if required.
		raise TOPException("RAM writing not supported on " + self.chipID)

__registeredChips = []

def getRegisteredChips():
	"Get a list of registered ChipDescriptions"
	return __registeredChips

class BitDescription:
	def __init__(self, bitNr, description):
		self.bitNr = bitNr
		self.description = description

class ChipDescription:
	# Possible chip types
	TYPE_MCU	= 0	# Microcontroller
	TYPE_EPROM	= 1	# EPROM
	TYPE_EEPROM	= 2	# EEPROM
	TYPE_GAL	= 3	# PAL/GAL
	TYPE_SRAM	= 4	# Static RAM
	TYPE_INTERNAL	= 999	# For internal use only

	def __init__(self, chipImplClass, bitfile, chipID="",
		     runtimeID=(0,0),
		     chipType=TYPE_MCU,
		     chipVendor=None,
		     description="", fuseDesc=(), lockbitDesc=(),
		     packages=None, comment="",
		     maintainer="Michael Buesch <mb@bu3sch.de>",
		     broken=False):
		"""Chip implementation class description.
		chipImplClass	=> The implementation class of the chip.
		bitfile		=> The bitfile ID string of the chip.
		chipID		=> The chip-ID string. Will default to the bitfile ID string.
		runtimeID	=> The runtime-ID is a tuple of two numbers that uniquely
				   identifies a loaded FPGA configuration. The first number in the
				   tuple is an ID number and the second number is a revision number.
		chipType	=> Chip type. Defaults to MCU.
		chipVendor	=> The chip vendor name(s).
		description	=> Human readable chip description string.
		fuseDesc	=> Tuple of fuse bits descriptions (BitDescription(), ...)
		lockbitDesc	=> Tuple of lock bits descriptions (BitDescription(), ...)
		packages	=> List of supported packages.
				   Each entry is a tuple of two strings: ("PACKAGE", "description")
		comment		=> Additional comment string.
		maintainer	=> Maintainer name.
		broken		=> Boolean flag to mark the implementation as broken.
		"""

		if not chipID:
			chipID = bitfile
		if type(chipVendor) == type(str()):
			chipVendor = (chipVendor, )
		self.chipImplClass = chipImplClass
		self.bitfile = bitfile
		self.chipID = chipID
		self.runtimeID = runtimeID
		self.chipType = chipType
		self.chipVendor = chipVendor
		self.description = description
		self.fuseDesc = fuseDesc
		self.lockbitDesc = lockbitDesc
		self.packages = packages
		self.comment = comment
		self.maintainer = maintainer
		self.broken = broken

		getRegisteredChips().append(self)

	@staticmethod
	def find(programmerType, chipID, allowBroken=False):
		"""Find chip implementations by ID and return a list of descriptors
		and instances of it."""
		found = []
		for chip in getRegisteredChips():
			if chip.broken and not allowBroken:
				continue
			if chip.chipID.lower().find(chipID.lower()) >= 0:
				instance = chip.chipImplClass()
				instance.registeredChip = chip
				instance.setChipID(chip.chipID)
				instance.setProgrammerType(programmerType)
				instance.generateVoltageLayouts()
				found.append( (chip, instance) )
		return found

	@staticmethod
	def findOne(programmerType, chipID, allowBroken=False):
		"""Find a chip implementation and return the descriptor
		and an instance of it. If chipID is not unique, this raises
		an exception"""
		found = ChipDescription.find(programmerType, chipID, allowBroken)
		if not found:
			raise TOPException("Did not find chipID \"%s\"" % chipID)
		if len(found) != 1:
			choices = map(lambda (desc, inst): desc.chipID, found)
			raise TOPException("The chipID \"%s\" is not unique. Choices are: %s" %\
				(chipID, ", ".join(choices)))
		return found[0]

	@staticmethod
	def dumpAll(fd, verbose=1, showBroken=True):
		"Dump all supported chips to file fd."
		count = 0
		for chip in getRegisteredChips():
			if chip.broken and not showBroken:
				continue
			if chip.chipType == ChipDescription.TYPE_INTERNAL:
				continue
			count = count + 1
			if count >= 2:
				fd.write("\n")
			chip.dump(fd, verbose)

	def dump(self, fd, verbose=1):
		"Dump information about a registered chip to file fd."
		if self.chipVendor:
			fd.write(", ".join(self.chipVendor) + "  ")
		if self.description:
			fd.write(self.description)
		else:
			fd.write(self.bitfile)
		extraFlags = []
		if not self.maintainer:
			extraFlags.append("Orphaned")
		if self.broken:
			extraFlags.append("Broken implementation")
		if extraFlags:
			fd.write("  (%s)" % "; ".join(extraFlags))
		fd.write("\n")
		if verbose >= 1:
			fd.write("%25s:  %s\n" % ("ChipID", self.chipID))
		if verbose >= 2:
			fd.write("%25s:  %s\n" % ("BIT-file", self.bitfile))
		if verbose >= 3 and self.packages:
			for (package, description) in self.packages:
				if description:
					description = "  (" + description + ")"
				fd.write("%25s:  %s%s\n" % ("Supported package", package, description))
		if verbose >= 4:
			supportedFeatures = (
				(Chip.SUPPORT_ERASE,		"Full chip erase"),
				(Chip.SUPPORT_SIGREAD,		"Chip signature reading"),
				(Chip.SUPPORT_PROGMEMREAD,	"Program memory reading (flash)"),
				(Chip.SUPPORT_PROGMEMWRITE,	"Program memory writing (flash)"),
				(Chip.SUPPORT_EEPROMREAD,	"(E)EPROM memory reading"),
				(Chip.SUPPORT_EEPROMWRITE,	"(E)EPROM memory writing"),
				(Chip.SUPPORT_FUSEREAD,		"Fuse bits reading"),
				(Chip.SUPPORT_FUSEWRITE,	"Fuse bits writing"),
				(Chip.SUPPORT_LOCKREAD,		"Lock bits reading"),
				(Chip.SUPPORT_LOCKWRITE,	"Lock bits writing"),
				(Chip.SUPPORT_RAMREAD,		"RAM reading"),
				(Chip.SUPPORT_RAMWRITE,		"RAM writing"),
				(Chip.SUPPORT_TEST,		"Unit-testing"),
			)
			supportFlags = Chip.getSupportFlags(self.chipImplClass)
			for (flag, description) in supportedFeatures:
				if flag & supportFlags:
					fd.write("%25s:  %s\n" % ("Support for", description))
		if verbose >= 2 and self.comment:
			fd.write("%25s:  %s\n" % ("Comment", self.comment))
		if verbose >= 3:
			maintainer = self.maintainer
			if not maintainer:
				maintainer = "NONE"
			fd.write("%25s:  %s\n" % ("Maintainer", maintainer))
