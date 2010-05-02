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
		Chip.__init__(self)

	def initializeChip(self):
		self.printDebug("Initializing chip")
		self.__reset()

	def shutdownChip(self):
		self.printDebug("Shutdown chip")
		self.__reset()

	def __reset(self):
		self.top.queueCommand("\x0E\x28\x00\x00")
		self.top.vccx.setLayoutPins( [] )
		self.vccxMask = 0
		self.top.vpp.setLayoutPins( [] )
		self.vppMask = 0
		self.top.gnd.setLayoutPins( [] )
		self.gndMask = 0
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(5)
		self.setOutputEnableMask(0)
		self.setOutputs(0)

	def setVCCX(self, voltage, layout):
		self.vccxMask = self.top.vccx.ID2mask(layout)
		self.__updateOutEn()
		self.top.cmdSetVCCXVoltage(0)
		self.top.cmdSetVCCXVoltage(voltage)
		self.top.vccx.setLayoutID(layout)
		self.top.flushCommands()

	def setVPP(self, voltage, layouts):
		self.vppMask = 0
		for layout in layouts:
			self.vppMask |= self.top.vpp.ID2mask(layout)
		self.__updateOutEn()
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(voltage)
		self.top.vpp.setLayoutMask(0)
		for layout in layouts:
			self.top.vpp.setLayoutID(layout)
		self.top.flushCommands()

	def setGND(self, layout):
		self.gndMask = self.top.gnd.ID2mask(layout)
		self.__updateOutEn()
		self.top.gnd.setLayoutID(0)
		self.top.flushCommands()

	def __updateOutEn(self):
		mask = self.desiredOutEnMask
		mask &= ~self.gndMask
		mask &= ~self.vccxMask
		mask &= ~self.vppMask
		self.top.cmdFPGAWrite(0x12, mask & 0xFF)
		self.top.cmdFPGAWrite(0x13, (mask >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x14, (mask >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x15, (mask >> 24) & 0xFF)
		self.top.cmdFPGAWrite(0x16, (mask >> 32) & 0xFF)
		self.top.cmdFPGAWrite(0x17, (mask >> 40) & 0xFF)
		self.top.flushCommands()

	def setOutputEnableMask(self, mask):
		self.desiredOutEnMask = mask
		self.__updateOutEn()

	def setOutputs(self, mask):
		self.top.cmdFPGAWrite(0x18, mask & 0xFF)
		self.top.cmdFPGAWrite(0x19, (mask >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x1A, (mask >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x1B, (mask >> 24) & 0xFF)
		self.top.cmdFPGAWrite(0x1C, (mask >> 32) & 0xFF)
		self.top.cmdFPGAWrite(0x1D, (mask >> 40) & 0xFF)
		self.top.flushCommands()

	def getInputs(self):
		self.top.cmdFPGAReadRaw(0x18)
		self.top.cmdFPGAReadRaw(0x19)
		self.top.cmdFPGAReadRaw(0x1A)
		self.top.cmdFPGAReadRaw(0x1B)
		self.top.cmdFPGAReadRaw(0x1C)
		self.top.cmdFPGAReadRaw(0x1D)
		inputs = self.top.cmdReadStatusReg48()
		return inputs

RegisteredChip(
	Chip_Unitest,
	bitfile = "unitest",
	runtimeID = (0x0008, 0x01),
	description = "Universal device tester",
)
