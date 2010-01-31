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
import time


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
		# First check if the chip is properly inserted
		self.top.blockCommands()
		self.top.cmdFlush()
		self.top.send("\x0A\x1D\x86")
		self.top.unblockCommands()

		self.top.cmdSetGNDPin(0)
		self.top.cmdLoadVPPLayout(0)
		self.top.cmdLoadVCCXLayout(0)

		self.top.blockCommands()
		self.top.cmdFlush(2)
		self.top.send("\x0A\x1B\xFF")
		self.top.unblockCommands()

		self.top.send("\x0E\x28\x00\x00")
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(5)
		self.top.cmdFlush(21)
		self.top.cmdLoadVPPLayout(14)

		self.top.blockCommands()
		self.top.cmdFlush(2)
		self.top.send("\x0B\x16")
		self.top.send("\x0B\x17")
		self.top.send("\x0B\x18")
		self.top.send("\x0B\x19")
		self.top.send("\x0B\x1A")
		self.top.send("\x0B\x1B")
		stat = self.top.cmdReadStatusReg32()
		self.top.unblockCommands()
		if stat != 0xFFFFFFC0:
			self.throwError("Did not detect chip. Please check connections.")

		self.top.cmdLoadVPPLayout(0)
		self.top.cmdLoadVCCXLayout(0)
		self.top.cmdFlush()
		self.top.send("\x0E\x28\x01\x00")
		self.top.send("\x0A\x1B\x00")
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(12)
		self.top.cmdFlush()
		self.top.cmdSetGNDPin(18)
		self.top.cmdFlush()
		self.top.cmdSetVCCXVoltage(4.4)
		self.top.cmdFlush()

		self.top.blockCommands()
		self.top.send("\x0A\x12\x05")
		self.top.send("\x0A\x12\x06")
		self.top.send("\x0A\x12\x04")
		self.top.send("\x0A\x12\x03")
		self.top.unblockCommands()

		self.top.cmdSetGNDPin(18)
		self.top.cmdLoadVCCXLayout(13)

		self.top.blockCommands()
		self.top.cmdFlush()
		self.top.send("\x19")
		self.top.send("\x0A\x12\x01\x34")
		self.top.send("\x0A\x12\x01")
		self.top.send("\x0A\x12\x02")
		self.top.send("\x0A\x12\x83")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x05")
		self.top.send("\x0A\x12\x06")
		self.top.send("\x0A\x12\x08")
		self.top.send("\x0A\x12\x04")
		self.top.send("\x0A\x12\x0A")
		self.top.send("\x0A\x12\x09")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87\x00")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07")
		self.top.send("\x0A\x12\x87")
		self.top.send("\x0A\x12\x07\x19")
		self.top.unblockCommands()

		self.top.cmdLoadVPPLayout(7)

		self.top.blockCommands()
		self.top.send("\x34")
		self.top.send("\x0A\x12\x88")
		self.top.cmdFlush()
		self.top.unblockCommands()

		self.top.cmdFlush(10)
		self.top.send("\x0E\x1F\x00\x00")
		time.sleep(0.1)
		stat = self.top.cmdReadStatusReg32()
		if stat != 0xB9C80101:
			self.throwError("read: Unexpected status value 0x%08X" % stat)

		# Now read the image
		self.printInfo("Reading image ", newline=False)
		image = ""
		self.top.send("\x0A\x12\x81")
		high = 0
		for chunk in range(0, 256, 2):
			if chunk % 8 == 0:
				percent = (chunk * 100 / 256)
				if percent % 25 == 0:
					self.printInfo("%d%%" % percent, newline=False)
				else:
					self.printInfo(".", newline=False)
			self.top.blockCommands()
			self.top.send("\x34")
			self.top.send("\x0A\x12\x01")
			self.top.send("\x0A\x12\x82")
			self.top.send("\x0A\x12\x04\x34")
			self.top.send("\x0A\x12\x05")
			self.top.send("\x0A\x12\x86\x10\x02")
			self.top.send("\x0A\x12\x87")
			self.top.send("\x0A\x12\x07")
			self.top.send("\x0A\x12\x05")
			self.top.send("\x0A\x12\x06\x10" + chr((chunk << 4) & 0xFF))
			self.top.send("\x0A\x12\x87")
			self.top.send("\x0A\x12\x07")
			self.top.send("\x0A\x12\x84")
			self.top.send("\x0A\x12\x05")
			self.top.send("\x0A\x12\x06\x10" + chr(high))
			self.top.send("\x0A\x12\x87")
			self.top.send("\x0A\x12\x07")
			self.top.send("\x0A\x12\x81")
			self.top.unblockCommands()
			for word in range(0, 31, 1):
				value = (chunk << 4) + (word + 1)
				high = (value >> 8) & 0xFF
				self.top.blockCommands()
				self.top.send("\x0A\x12\x04")
				self.top.send("\x0A\x12\x02\x01")
				self.top.send("\x0A\x12\x84\x01")
				self.top.send("\x0A\x12\x82")
				self.top.send("\x0A\x12\x01\x34")
				self.top.send("\x0A\x12\x01")
				self.top.send("\x0A\x12\x82")
				self.top.send("\x0A\x12\x04\x34")
				self.top.send("\x0A\x12\x05")
				self.top.send("\x0A\x12\x86\x10\x02")
				self.top.send("\x0A\x12\x87")
				self.top.send("\x0A\x12\x07")
				self.top.send("\x0A\x12\x05")
				self.top.send("\x0A\x12\x06\x10" + chr(value & 0xFF))
				self.top.send("\x0A\x12\x87")
				self.top.send("\x0A\x12\x07")
				self.top.send("\x0A\x12\x84")
				self.top.send("\x0A\x12\x05\x00\x00")
				self.top.send("\x0A\x12\x06\x10" + chr(high))
				self.top.send("\x0A\x12\x87")
				self.top.send("\x0A\x12\x07")
				self.top.send("\x0A\x12\x81")
				self.top.unblockCommands()
			self.top.blockCommands()
			self.top.send("\x0A\x12\x04")
			self.top.send("\x0A\x12\x02\x01")
			self.top.send("\x0A\x12\x84\x01")
			self.top.send("\x0A\x12\x82")
			self.top.send("\x0A\x12\x01\x07")
			self.top.unblockCommands()
			data = self.top.cmdReadStatusReg()
			image += data
		self.printInfo("100%")
		return image

	def writeImage(self, image):
		pass#TODO

supportedChips.append(ATMega8DIP28())
