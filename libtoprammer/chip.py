"""
#    TOP2049 Open Source programming suite
#
#    Chip support
#
#    Copyright (c) 2009-2017 Michael Buesch <m@bues.ch>
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
from generic_algorithms import *
from ihex import *


class Chip(object):
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
	SUPPORT_UILREAD		= (1 << 13)
	SUPPORT_UILWRITE	= (1 << 14)

	@classmethod
	def chipSupportsAttr(cls, methodName):
		"""Check if a chip implementation supports a feature.
		'methodName' is the class member function to check for"""
		# This works by checking whether the subclass overloaded
		# the member function attribute.
		return getattr(cls, methodName) != getattr(Chip, methodName)

	@classmethod
	def getSupportFlags(cls):
		"Get the SUPPORT_... flags for this chip"
		flags = 0
		for (methodName, flag) in (
				("erase",		cls.SUPPORT_ERASE),
				("readSignature",	cls.SUPPORT_SIGREAD),
				("readProgmem",		cls.SUPPORT_PROGMEMREAD),
				("writeProgmem",	cls.SUPPORT_PROGMEMWRITE),
				("readEEPROM",		cls.SUPPORT_EEPROMREAD),
				("writeEEPROM",		cls.SUPPORT_EEPROMWRITE),
				("readFuse",		cls.SUPPORT_FUSEREAD),
				("writeFuse",		cls.SUPPORT_FUSEWRITE),
				("readLockbits",	cls.SUPPORT_LOCKREAD),
				("writeLockbits",	cls.SUPPORT_LOCKWRITE),
				("readRAM",		cls.SUPPORT_RAMREAD),
				("writeRAM",		cls.SUPPORT_RAMWRITE),
				("test",		cls.SUPPORT_TEST),
				("readUserIdLocation",	cls.SUPPORT_UILREAD),
				("writeUserIdLocation",		cls.SUPPORT_UILWRITE)):
			
			if cls.chipSupportsAttr(methodName):
				flags |= flag
		return flags

	@classmethod
	def createInstance(cls, top, chipDescription, assignedChipOptions=()):
		instance = cls()
		instance.top = top
		instance.chipDescription = chipDescription
		for acopt in assignedChipOptions:
			copt = chipDescription.getChipOption(acopt.name)
			if not copt:
				raise TOPException("'%s' is not a valid chip option "
					"for chip ID '%s'" %\
					(acopt.name, chipDescription.chipID))
			acopt.detectAndVerifyType(copt)
		instance.assignedChipOptions = assignedChipOptions
		instance.generateVoltageLayouts()
		return instance

	def __init__(self, chipPackage=None, chipPinVCC=None, chipPinsVPP=None, chipPinGND=None):
		"""chipPackage is the ID string for the package.
		May be None, if no initial auto-layout is required.
		chipPinVCC is the required VCC pin on the package.
		chipPinsVPP is the required VPP pin on the package.
		chipPinGND is the required GND pin on the package."""

		self.__chipPackage = chipPackage
		self.__chipPinVCC = chipPinVCC
		self.__chipPinsVPP = chipPinsVPP
		self.__chipPinGND = chipPinGND

	def printWarning(self, message):
		self.top.printWarning(self.chipDescription.chipID +\
				      ": Warning - " + message)

	def printInfo(self, message):
		self.top.printInfo(self.chipDescription.chipID +\
				   ": " + message)

	def printDebug(self, message):
		self.top.printDebug(self.chipDescription.chipID +\
				    ": Debug - " + message)

	def throwError(self, message, always=False):
		message = self.chipDescription.chipID + ": " + message
		if self.top.getForceLevel() >= 1 and not always:
			self.printWarning(message)
		else:
			raise TOPException(message)

	def generateVoltageLayouts(self):
		if self.__chipPackage:
			self.generator = createLayoutGenerator(self.__chipPackage)
			self.generator.setProgrammerType(self.top.getProgrammerType())
			self.generator.setPins(vccPin=self.__chipPinVCC,
					       vppPins=self.__chipPinsVPP,
					       gndPin=self.__chipPinGND)
			self.generator.recalculate()

	def getLayoutGenerator(self):
		if self.__chipPackage:
			return self.generator
		return None

	def applyVCC(self, turnOn):
		"Turn VCC on, using the auto-layout."
		if turnOn:
			try:
				generator = self.generator
			except (AttributeError), e:
				self.throwError("BUG: Using auto-layout, but did not initialize it.",
						always=True)
			generator.applyVCCLayout(self.top)
		else:
			self.top.vcc.setLayoutMask(0)

	def applyVPP(self, turnOn, packagePinsToTurnOn=[]):
		"""Turn VPP on, using the auto-layout.
		packagePinsToTurnOn is a list of pins on the package to drive to VPP.
		If it is not passed (or an empty list), all VPP pins of the layout are turned on.
		The parameter is unused, if turnOn=False."""
		if turnOn:
			try:
				generator = self.generator
			except (AttributeError), e:
				self.throwError("BUG: Using auto-layout, but did not initialize it.",
						always=True)
			generator.applyVPPLayout(self.top, packagePinsToTurnOn)
		else:
			self.top.vpp.setLayoutMask(0)

	def applyGND(self, turnOn):
		"Turn GND on, using the auto-layout."
		if turnOn:
			try:
				generator = self.generator
			except (AttributeError), e:
				self.throwError("BUG: Using auto-layout, but did not initialize it.",
						always=True)
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

	def getChipOptionValue(self, name, default=None):
		"""Get an AssignedChipOption value that was set by the user.
		If no such option is found, it returns 'default'."""
		name = name.lower()
		for acopt in self.assignedChipOptions:
			if acopt.name.lower() == name:
				return acopt.value
		return default

	def shutdownChip(self):
		# Override me in the subclass, if required.
		self.printDebug("Default chip shutdown")
		GenericAlgorithms(self).simpleVoltageShutdown()

	def getIHexInterpreter(self):
		# Returns the IHEX file interpreter.
		# This defaults to the non-section interpreter.
		# Override me in the subclass, if required.
		return IHexInterpreter()

	def readSignature(self):
		# Override me in the subclass, if required.
		self.throwError("Signature reading not supported",
				always=True)

	def erase(self):
		# Override me in the subclass, if required.
		self.throwError("Chip erasing not supported",
				always=True)

	def test(self):
		# Override me in the subclass, if required.
		self.throwError("Chip testing not supported",
				always=True)

	def readProgmem(self):
		# Override me in the subclass, if required.
		self.throwError("Program memory reading not supported",
				always=True)

	def writeProgmem(self, image):
		# Override me in the subclass, if required.
		self.throwError("Program memory writing not supported",
				always=True)

	def readEEPROM(self):
		# Override me in the subclass, if required.
		self.throwError("EEPROM reading not supported",
				always=True)

	def writeEEPROM(self, image):
		# Override me in the subclass, if required.
		self.throwError("EEPROM writing not supported",
				always=True)

	def readFuse(self):
		# Override me in the subclass, if required.
		self.throwError("Fuse reading not supported",
				always=True)

	def writeFuse(self, image):
		# Override me in the subclass, if required.
		self.throwError("Fuse writing not supported",
				always=True)

	def readLockbits(self):
		# Override me in the subclass, if required.
		self.throwError("Lockbit reading not supported",
				always=True)

	def writeLockbits(self, image):
		# Override me in the subclass, if required.
		self.throwError("Lockbit writing not supported",
				always=True)

	def readRAM(self):
		# Override me in the subclass, if required.
		self.throwError("RAM reading not supported",
				always=True)

	def writeRAM(self, image):
		# Override me in the subclass, if required.
		self.throwError("RAM writing not supported",
				always=True)
		
	def readUserIdLocation(self):
		# Override me in the subclass, if required.
		self.throwError("User ID Location reading not supported",
				always=True)

	def writeUserIdLocation(self, image):
		# Override me in the subclass, if required.
		self.throwError("User ID Location writing not supported",
				always=True)

__registeredChips = []

def getRegisteredChips():
	"Get a list of registered ChipDescriptions"
	return __registeredChips

def getRegisteredVendors():
	"Returns a dict of 'vendor : [descriptor, ...]' "
	vendors = { }
	for descriptor in getRegisteredChips():
		for vendor in descriptor.chipVendors:
			vendors.setdefault(vendor, []).append(descriptor)
	return vendors

def _registerChip(chipDesc):
	regList = getRegisteredChips()
	if chipDesc.chipID in [ cd.chipID for cd in regList ]:
		raise TOPException("Chip description registration: "
			"The chipID '%s' is not unique." %\
			chipDesc.chipID)
	regList.append(chipDesc)

class BitDescription:
	def __init__(self, bitNr, description):
		self.bitNr = bitNr
		self.description = description

class ChipOption(object):
	TYPE_UNKNOWN	= "unknown"
	TYPE_BOOL	= "bool"
	TYPE_INT	= "int"
	TYPE_FLOAT	= "float"

	def __init__(self, optType, name, description=""):
		self.optType = optType
		self.name = name
		self.description = description

	def __repr__(self):
		desc = " / " + self.description if self.description else ""
		return "%s (%s%s)" % (self.name, self.optType, desc)

	def castValue(self, string):
		return None

class ChipOptionBool(ChipOption):
	def __init__(self, name, description=""):
		ChipOption.__init__(self, ChipOption.TYPE_BOOL,
				    name, description)

	def castValue(self, string):
		return str2bool(string)

class ChipOptionInt(ChipOption):
	def __init__(self, name, description="", minVal=None, maxVal=None):
		ChipOption.__init__(self, ChipOption.TYPE_INT,
				    name, description)
		self.minVal = int(minVal) if minVal is not None else None
		self.maxVal = int(maxVal) if minVal is not None else None

	def __limitError(self, value):
		raise TOPException("%s: Value exceeds limits: %d <= %d <= %d" %\
			(self.name, self.minVal, value, self.maxVal))

	def castValue(self, string):
		try:
			value = int(string)
		except (ValueError), e:
			return None
		if (self.minVal is not None and value < self.minVal) or\
		   (self.maxVal is not None and value > self.maxVal):
			self.__limitError(value)
		return value

class ChipOptionFloat(ChipOption):
	def __init__(self, name, description="", minVal=None, maxVal=None):
		ChipOption.__init__(self, ChipOption.TYPE_FLOAT,
				    name, description)
		self.minVal = float(minVal) if minVal is not None else None
		self.maxVal = float(maxVal) if minVal is not None else None

	def __limitError(self, value):
		raise TOPException("%s: Value exceeds limits: %f <= %f <= %f" %\
			(self.name, self.minVal, value, self.maxVal))

	def castValue(self, string):
		try:
			value = float(string)
		except (ValueError), e:
			return None
		if (self.minVal is not None and value < self.minVal) or\
		   (self.maxVal is not None and value > self.maxVal):
			self.__limitError(value)
		return value

class AssignedChipOption(ChipOption):
	def __init__(self, name, value):
		ChipOption.__init__(self, ChipOption.TYPE_UNKNOWN, name)
		self.value = value

	def detectAndVerifyType(self, baseOption):
		assert(baseOption.optType != self.TYPE_UNKNOWN)
		if self.optType != self.TYPE_UNKNOWN:
			return
		value = baseOption.castValue(self.value)
		if value is None:
			raise TOPException("Chip option '%s' type mismatch. "
				"Must be '%s'." %\
				(self.name, baseOption.optType))
		self.optType = baseOption.optType
		self.value = value

class ChipDescription:
	# Possible chip types
	TYPE_MCU	= 0	# Microcontroller
	TYPE_EPROM	= 1	# EPROM
	TYPE_EEPROM	= 2	# EEPROM
	TYPE_GAL	= 3	# PAL/GAL
	TYPE_SRAM	= 4	# Static RAM
	TYPE_LOGIC	= 5	# Logics chip
	TYPE_INTERNAL	= 999	# For internal use only

	def __init__(self, chipImplClass, bitfile, chipID="",
		     runtimeID=(0,0),
		     chipType=TYPE_MCU,
		     chipVendors="Other",
		     description="", fuseDesc=(), lockbitDesc=(),
		     packages=None, comment="",
		     chipOptions=(),
		     maintainer="Michael Buesch <m@bues.ch>",
		     broken=False):
		"""Chip implementation class description.
		chipImplClass	=> The implementation class of the chip.
		bitfile		=> The name of the default bitfile loaded on initialization.
		chipID		=> The chip-ID string. Will default to the bitfile ID string.
		runtimeID	=> The runtime-ID is a tuple of two numbers that uniquely
				   identifies a loaded FPGA configuration. The first number in the
				   tuple is an ID number and the second number is a revision number.
		chipType	=> Chip type. Defaults to MCU.
		chipVendors	=> The chip vendor name(s).
		description	=> Human readable chip description string.
		fuseDesc	=> Tuple of fuse bits descriptions (BitDescription(), ...)
		lockbitDesc	=> Tuple of lock bits descriptions (BitDescription(), ...)
		packages	=> List of supported packages.
				   Each entry is a tuple of two strings: ("PACKAGE", "description")
		comment		=> Additional comment string.
		chipOptions	=> Tuple of ChipOption instances, if any.
		maintainer	=> Maintainer name.
		broken		=> Boolean flag to mark the implementation as broken.
		"""

		if not chipID:
			chipID = bitfile
		if isinstance(chipVendors, str):
			chipVendors = (chipVendors, )
		self.chipImplClass = chipImplClass
		self.bitfile = bitfile
		self.chipID = chipID
		self.runtimeID = runtimeID
		self.chipType = chipType
		self.chipVendors = chipVendors
		self.description = description
		self.fuseDesc = fuseDesc
		self.lockbitDesc = lockbitDesc
		self.packages = packages
		self.comment = comment
		self.chipOptions = chipOptions
		self.maintainer = maintainer
		self.broken = broken

		_registerChip(self)

	@classmethod
	def findAll(cls, chipID, allowBroken=False):
		"Find all ChipDescriptions by fuzzy chipID match."
		found = [ chipDesc for chipDesc in getRegisteredChips() if (
			(not chipDesc.broken or allowBroken) and\
			(chipDesc.chipID.lower().find(chipID.lower()) >= 0)
		) ]
		return found

	@classmethod
	def findOne(cls, chipID, allowBroken=False):
		"""Find a chip implementation and return the ChipDescriptor.
		Raise an exception, if chipID is not unique."""
		found = cls.findAll(chipID, allowBroken)
		if not found:
			raise TOPException("Did not find chipID \"%s\"" % chipID)
		if len(found) != 1:
			choices = [ desc.chipID for desc in found ]
			raise TOPException(
				"The chipID \"%s\" is not unique. Choices are: %s" %\
				(chipID, ", ".join(choices)))
		return found[0]

	@classmethod
	def dumpAll(cls, fd, verbose=1, showBroken=True):
		"Dump all supported chips to file fd."
		count = 0
		for chip in getRegisteredChips():
			if chip.broken and not showBroken:
				continue
			if chip.chipType == cls.TYPE_INTERNAL:
				continue
			count = count + 1
			if count >= 2:
				fd.write("\n")
			chip.dump(fd, verbose)

	def dump(self, fd, verbose=1):
		"Dump information about a registered chip to file fd."

		if verbose <= 0:
			fd.write(self.chipID)
			return

		def wrline(prefix, content):
			# Write a formatted feature line
			fd.write("%15s:  %s\n" % (prefix, content))

		banner = ""
		if self.chipVendors:
			banner += ", ".join(self.chipVendors) + "  "
		if self.description:
			banner += self.description
		else:
			banner += self.bitfile
		extraFlags = []
		if not self.maintainer:
			extraFlags.append("Orphaned")
		if self.broken:
			extraFlags.append("Broken implementation")
		if extraFlags:
			banner += "  (%s)" % "; ".join(extraFlags)
		sep = '+' + '-' * (len(banner) + 4) + '+\n'
		fd.write(sep + '|  ' + banner + '  |\n' + sep)

		if verbose >= 1:
			wrline("Chip ID", self.chipID)
		if verbose >= 2:
			bitfile = self.bitfile
			if not bitfile.endswith('.bit'):
				bitfile += '.bit'
			wrline("BIT file", bitfile)
		if verbose >= 1:
			for opt in self.chipOptions:
				wrline("Chip option", str(opt))
		if verbose >= 3 and self.packages:
			for (package, description) in self.packages:
				if description:
					description = "  (" + description + ")"
				wrline("Chip package", package + description)
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
				(Chip.SUPPORT_UILMREAD,		"User ID Location reading"),
				(Chip.SUPPORT_UILWRITE,		"User ID Location writing"),
			)
			supportFlags = self.chipImplClass.getSupportFlags()
			for (flag, description) in supportedFeatures:
				if flag & supportFlags:
					wrline("Support for", description)
		if verbose >= 2 and self.comment:
			wrline("Comment", self.comment)
		if verbose >= 3:
			maintainer = self.maintainer
			if not maintainer:
				maintainer = "NONE"
			wrline("Maintainer", maintainer)

	def getChipOption(self, name):
		"Get a ChipOption by case insensitive 'name'."
		name = name.lower()
		for opt in self.chipOptions:
			if opt.name.lower() == name:
				return opt
		return None
