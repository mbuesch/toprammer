"""
#    TOP2049 Open Source programming suite
#
#    Chip support
#
#    Copyright (c) 2009-2010 Michael Buesch <mb@bu3sch.de>
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


supportedChips = []

class Chip:
	def __init__(self, chipID):
		"The chipID is the ID string from the bitfile."
		self.chipID = chipID
		self.printPrefix = True

	def getID(self):
		return self.chipID

	def setTOP(self, top):
		self.top = top

	def printInfo(self, message, newline=True):
		if self.printPrefix:
			message = self.chipID + ": " + message
		self.top.printInfo(message, newline)
		self.printPrefix = newline

	def printDebug(self, message, newline=True):
		if self.printPrefix:
			message = self.chipID + ": " + message
		self.top.printDebug(message, newline)
		self.printPrefix = newline

	def throwError(self, message):
		raise TOPException(self.chipID + ": " + message)

	def initializeChip(self):
		pass # Override me in the subclass, if required.

	def readSignature(self):
		# Override me in the subclass, if required.
		raise TOPException("Signature reading not supported on " + self.chipID)

	def erase(self):
		# Override me in the subclass, if required.
		raise TOPException("Chip erasing not supported on " + self.chipID)

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

def chipFind(chipID):
	for chip in supportedChips:
		if chip.getID().lower() == chipID.lower():
			return chip
	return None
