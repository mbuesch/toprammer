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

	def getID(self):
		return self.chipID

	def setTOP(self, top):
		self.top = top

	def printInfo(self, message):
		self.top.printInfo(self.chipID + ": " + message)

	def printDebug(self, message):
		self.top.printDebug(self.chipID + ": " + message)

	def throwError(self, message):
		raise TOPException(self.chipID + ": " + message)

	def initializeChip(self):
		pass # Override me in the subclass, if required.

	def readImage(self):
		# Override me in the subclass, if required.
		raise TOPException("Image reading not supported on " + self.chipID)

	def writeImage(self, image):
		# Override me in the subclass, if required.
		raise TOPException("Image writing not supported on " + self.chipID)

def chipFind(chipID):
	for chip in supportedChips:
		if chip.getID().lower() == chipID.lower():
			return chip
	return None
