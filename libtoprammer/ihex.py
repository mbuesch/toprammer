"""
#    TOP2049 Open Source programming suite
#
#    IHEX file layout
#
#    Copyright (c) 2013 Michael Buesch <m@bues.ch>
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


class AddressRange(object):
	"""Address range type."""

	def __init__(self, startAddress = 0, endAddress = -1):
		# endAddress of -1 means "to the end of the image".
		assert(startAddress >= 0)
		assert(endAddress >= -1)
		assert(startAddress <= endAddress or endAddress == -1)
		self.startAddress = startAddress
		self.endAddress = endAddress

	def overlaps(self, other):
		"""Check if self overlaps with other."""
		if (other.startAddress <= self.endAddress or self.endAddress < 0) and\
		   (other.endAddress >= self.startAddress or other.endAddress < 0):
			return True
		return False

	@classmethod
	def overlapsAny(cls, addressRangeList, addressRange):
		"""Check if 'addressRange' overlaps with any
		AddressRange in 'addressRangeList'"""
		return any(r.overlaps(addressRange) for r in addressRangeList)

class IHexInterpreter(object):
	"""Generic interpreter for a cumulative IHEX file.
	This class must be subclassed to be usable."""

	# Definition of the address ranges.
	# For each memory area type, several possible address
	# ranges can be defined. They are tried first to last.
	# Override these in the subclass.
	progmemRanges = None
	eepromRanges = None
	fuseRanges = None
	lockRanges = None
	ramRanges = None
	uilRanges = None

	# Definition of default memory values.
	# Override these in the subclass.
	progmemDefaultBytes = b"\xFF"
	eepromDefaultBytes = b"\xFF"
	fuseDefaultBytes = b"\xFF"
	lockDefaultBytes = b"\xFF"
	ramDefaultBytes = b"\x00"
	uilDefaultBytes = b"\xFF"

	def __init__(self):
		self.__ihexData = None
		self.__progmem = None
		self.__eeprom = None
		self.__fusebits = None
		self.__lockbits = None
		self.__ram = None
		self.__uil = None

	def cumulativeSupported(self):
		"""Returns True, if parsing of cumulative IHEX files
		is supported by the implementation."""
		return self.progmemRanges or\
		       self.eepromRanges or\
		       self.fuseRanges or\
		       self.lockRanges or\
		       self.ramRanges or\
		       self.uilRanges

	def interpret(self, ihexData):
		self.__ihexData = ihexData
		usedRanges = []
		self.__progmem = self.tryExtract(ihexData, self.progmemDefaultBytes,
						 usedRanges, self.progmemRanges)
		self.__eeprom = self.tryExtract(ihexData, self.eepromDefaultBytes,
						usedRanges, self.eepromRanges)
		self.__fusebits = self.tryExtract(ihexData, self.fuseDefaultBytes,
						  usedRanges, self.fuseRanges)
		self.__lockbits = self.tryExtract(ihexData, self.lockDefaultBytes,
						  usedRanges, self.lockRanges)
		self.__ram = self.tryExtract(ihexData, self.ramDefaultBytes,
					     usedRanges, self.ramRanges)
		self.__uil = self.tryExtract(ihexData, self.uilDefaultBytes,
					     usedRanges, self.uilRanges)

	def tryExtract(self, ihexData, defaultBytes, alreadyUsedRanges, tryRanges):
		if not tryRanges:
			return None
		for tryRange in tryRanges:
			if AddressRange.overlapsAny(alreadyUsedRanges, tryRange):
				continue
			image = IO_ihex().toBinary(ihexData,
						   addressRange = tryRange,
						   defaultBytes = defaultBytes)
			if not image:
				continue
			alreadyUsedRanges.append(tryRange)
			return image
		return None

	def getRaw(self, defaultBytes=b"\xFF"):
		return IO_ihex().toBinary(self.__ihexData,
					  defaultBytes = defaultBytes)

	def getProgmem(self, dontInterpretSections=False):
		if dontInterpretSections:
			return self.getRaw(defaultBytes = self.progmemDefaultBytes)
		return self.__progmem

	def getEEPROM(self, dontInterpretSections=False):
		if dontInterpretSections:
			return self.getRaw(defaultBytes = self.eepromDefaultBytes)
		return self.__eeprom

	def getFusebits(self, dontInterpretSections=False):
		if dontInterpretSections:
			return self.getRaw(defaultBytes = self.fuseDefaultBytes)
		return self.__fusebits

	def getLockbits(self, dontInterpretSections=False):
		if dontInterpretSections:
			return self.getRaw(defaultBytes = self.lockDefaultBytes)
		return self.__lockbits

	def getRAM(self, dontInterpretSections=False):
		if dontInterpretSections:
			return self.getRaw(defaultBytes = self.ramDefaultBytes)
		return self.__ram

	def getUIL(self, dontInterpretSections=False):
		if dontInterpretSections:
			return self.getRaw(defaultBytes = self.uilDefaultBytes)
		return self.__uil
