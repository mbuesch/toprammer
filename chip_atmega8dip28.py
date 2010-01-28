"""
#    TOP2049 Open Source programming suite
#
#    Atmel Mega8 DIP28 support
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

from chip import *


class ATMega8DIP28(Chip):
	def __init__(self):
		Chip.__init__(self, "atmega8dip28")

	def initializeChip(self):
		self.top.cmdSetGNDPin(18)
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(12)

	def readImage(self):
		pass#TODO
		return "Fooobar"

	def writeImage(self, image):
		pass#TODO

supportedChips.append(ATMega8DIP28())
