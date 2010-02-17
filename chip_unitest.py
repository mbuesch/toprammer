"""
#    TOP2049 Open Source programming suite
#
#    Universal device tester
#
#    Copyright (c) 2010 Michael Buesch <mb@bu3sch.de>
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


class Chip_Unitest(Chip):
	def __init__(self):
		Chip.__init__(self, "unitest")

	def initializeChip(self):
		self.printDebug("Initializing chip")
		self.__reset()

	def shutdownChip(self):
		self.printDebug("Shutdown chip")
		self.__reset()

	def __reset(self):
		self.top.vccx.setLayoutPins( [] )
		self.top.vpp.setLayoutPins( [] )
		self.top.gnd.setLayoutPins( [] )
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(5)
		self.setOutputEnableMask(0)
		self.setOutputs(0)

	def setVCCX(self, voltage, layout):
		self.top.blockCommands()
		self.top.cmdSetVCCXVoltage(0)
		self.top.cmdLoadVCCXLayout(layout)
		self.top.cmdSetVCCXVoltage(voltage)
		self.top.unblockCommands()

	def setVPP(self, voltage, layout):
		self.top.blockCommands()
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdLoadVPPLayout(layout)
		self.top.cmdSetVPPVoltage(voltage)
		self.top.unblockCommands()
		#TODO: Disable outen on these pins

	def setGND(self, pin):
		self.top.blockCommands()
		self.top.cmdSetGNDPin(pin)
		self.top.unblockCommands()

	def setOutputEnableMask(self, mask):
		self.top.blockCommands()
		self.top.cmdFPGAWrite(0x12, mask & 0xFF)
		self.top.cmdFPGAWrite(0x13, (mask >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x14, (mask >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x15, (mask >> 24) & 0xFF)
		self.top.cmdFPGAWrite(0x16, (mask >> 32) & 0xFF)
		self.top.cmdFPGAWrite(0x17, (mask >> 40) & 0xFF)
		self.top.unblockCommands()

	def setOutputs(self, mask):
		self.top.blockCommands()
		self.top.cmdFPGAWrite(0x18, mask & 0xFF)
		self.top.cmdFPGAWrite(0x19, (mask >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x1A, (mask >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x1B, (mask >> 24) & 0xFF)
		self.top.cmdFPGAWrite(0x1C, (mask >> 32) & 0xFF)
		self.top.cmdFPGAWrite(0x1D, (mask >> 40) & 0xFF)
		self.top.unblockCommands()

	def getInputs(self):
		self.top.blockCommands()
		self.top.cmdFPGAReadRaw(0x18)
		self.top.cmdFPGAReadRaw(0x19)
		self.top.cmdFPGAReadRaw(0x1A)
		self.top.cmdFPGAReadRaw(0x1B)
		self.top.cmdFPGAReadRaw(0x1C)
		self.top.cmdFPGAReadRaw(0x1D)
		inputs = self.top.cmdReadStatusReg48()
		self.top.unblockCommands()
		return inputs

supportedChips.append(Chip_Unitest())
