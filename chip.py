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
	def __init__(self, chipID, broken=False):
		"The chipID is the ID string from the bitfile."
		self.chipID = chipID
		self.broken = broken
		self.printPrefix = True

	def getID(self):
		return self.chipID

	def isBroken(self):
		return self.broken

	def setTOP(self, top):
		self.top = top

	def printWarning(self, message, newline=True):
		if self.printPrefix:
			message = self.chipID + ": " + message
		self.top.printWarning(message, newline)
		self.printPrefix = newline

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

	def progressMeterInit(self, message, nrSteps):
		self.progressNrSteps = nrSteps
		self.progressHave25 = False
		self.progressHave50 = False
		self.progressHave75 = False
		self.printInfo(message + " [0%", newline=False)

	def progressMeterFinish(self):
		if not self.progressNrSteps:
			self.printInfo("...", newline=False)
		self.printInfo("100%]")

	def progressMeter(self, step):
		if step % (self.progressNrSteps // 32) == 0:
			percent = (step * 100 // self.progressNrSteps)
			if percent >= 25 and not self.progressHave25:
				self.printInfo("25%", newline=False)
				self.progressHave25 = True
			elif percent >= 50 and not self.progressHave50:
				self.printInfo("50%", newline=False)
				self.progressHave50 = True
			elif percent >= 75 and not self.progressHave75:
				self.printInfo("75%", newline=False)
				self.progressHave75 = True
			else:
				self.printInfo(".", newline=False)

	def initializeChip(self):
		pass # Override me in the subclass, if required.

	def shutdownChip(self):
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

	def readLockbits(self):
		# Override me in the subclass, if required.
		raise TOPException("Lockbit reading not supported on " + self.chipID)

	def writeLockbits(self, image):
		# Override me in the subclass, if required.
		raise TOPException("Lockbit writing not supported on " + self.chipID)

def chipFind(chipID):
	for chip in supportedChips:
		if chip.getID().lower() == chipID.lower():
			return chip
	return None
