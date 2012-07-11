"""
#    TOP2049 Open Source programming suite
#
#    Universal device tester
#
#    Copyright (c) 2010-2012 Michael Buesch <m@bues.ch>
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

from libtoprammer.chip import *


class Chip_Unitest(Chip):
	MODE_UNITEST	= 0	# Standard universal tester
	MODE_FCNT	= 1	# Frequency counter

	def __init__(self, chipPackage=None, chipPinVCC=None, chipPinsVPP=None, chipPinGND=None,
			   VCCVoltage=None, VPPVoltage=None):
		Chip.__init__(self, chipPackage=chipPackage, chipPinVCC=chipPinVCC,
			      chipPinsVPP=chipPinsVPP, chipPinGND=chipPinGND)
		self.autogenVCCVoltage = VCCVoltage
		self.autogenVPPVoltage = VPPVoltage
		self.mode = self.MODE_UNITEST

	def shutdownChip(self):
		self.printDebug("Shutdown chip")
		self.reset()

	def reset(self):
		self.top.vcc.setLayoutPins( [] )
		self.vccMask = 0
		self.top.vpp.setLayoutPins( [] )
		self.vppMask = 0
		self.top.gnd.setLayoutPins( [] )
		self.gndMask = 0
		self.top.cmdSetVCCVoltage(self.top.vcc.minVoltage())
		self.top.cmdSetVPPVoltage(self.top.vpp.minVoltage())
		self.oscMask = 0
		self.oscDiv = 0
		self.fcntPin = 0
		self.setOutputEnableMask(0)
		self.setOutputs(0)
		self.setOscMask(0)
		self.top.flushCommands()

	def getMode(self):
		return self.mode

	def setMode(self, newMode):
		if self.mode == newMode:
			return
		# Upload the new bitfile to the FPGA
		bitfiles = {
			self.MODE_UNITEST	: ("unitest", (8, 1)),
			self.MODE_FCNT		: ("unitest_fcnt", (8, 2)),
		}
		name, runtimeIDs = bitfiles[newMode]
		self.top.configureFPGA(name, runtimeIDs)
		# Re-upload the FPGA state
		self.__updateOutEn()
		self.__updateOut()
		self.__updateOscDivider()
		self.__updateOscMask()
		self.__updateFreqCountPin()
		self.top.flushCommands()
		self.mode = newMode

	def setVCC(self, voltage, layout):
		self.vccMask = self.top.vcc.ID2mask(layout)
		self.__updateOutEn()
		self.top.cmdSetVCCVoltage(voltage)
		self.top.vcc.setLayoutID(layout)
		self.top.flushCommands()

	def setVPP(self, voltage, layouts):
		self.vppMask = 0
		for layout in layouts:
			self.vppMask |= self.top.vpp.ID2mask(layout)
		self.__updateOutEn()
		self.top.cmdSetVPPVoltage(voltage)
		self.top.vpp.setLayoutMask(0) # Reset
		for layout in layouts:
			self.top.vpp.setLayoutID(layout)
		self.top.flushCommands()

	def setGND(self, layout):
		self.gndMask = self.top.gnd.ID2mask(layout)
		self.__updateOutEn()
		self.top.gnd.setLayoutID(layout)
		self.top.flushCommands()

	# Overloaded layout generator interface.
	def applyVCC(self, turnOn):
		layoutID = 0
		if turnOn:
			(layoutID, layoutMask) = self.generator.getVCCLayout()
		self.setVCC(self.autogenVCCVoltage, layoutID)

	# Overloaded layout generator interface.
	def applyVPP(self, turnOn, packagePinsToTurnOn=[]):
		assert(not packagePinsToTurnOn) # Not supported, yet.
		layouts = []
		if turnOn:
			layouts = map(lambda (layoutID, layoutMask): layoutID,
				      self.generator.getVPPLayouts())
		self.setVPP(self.autogenVPPVoltage, layouts)

	# Overloaded layout generator interface.
	def applyGND(self, turnOn):
		layoutID = 0
		if turnOn:
			(layoutID, layoutMask) = self.generator.getGNDLayout()
		self.setGND(layoutID)

	def getActivePinMask(self):
		masks = {
			self.MODE_UNITEST	: 0xFFFFFFFFFFFF, # 1-48
			self.MODE_FCNT		: 0x000FFFFFF000, # 13-36
		}
		return masks[self.mode]

	def __updateOutEn(self):
		mask = self.desiredOutEnMask
		mask &= ~self.gndMask
		mask &= ~self.vccMask
		mask &= ~self.vppMask
		mask |= self.oscMask
		mask &= self.getActivePinMask()
		self.top.cmdFPGAWrite(0x40, mask & 0xFF)
		self.top.cmdFPGAWrite(0x41, (mask >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x42, (mask >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x43, (mask >> 24) & 0xFF)
		self.top.cmdFPGAWrite(0x44, (mask >> 32) & 0xFF)
		self.top.cmdFPGAWrite(0x45, (mask >> 40) & 0xFF)

	def setOutputEnableMask(self, mask):
		self.desiredOutEnMask = mask
		self.__updateOutEn()
		self.top.flushCommands()

	def __updateOut(self):
		mask = self.desiredOutMask
		mask &= ~self.oscMask
		mask &= self.getActivePinMask()
		self.top.cmdFPGAWrite(0x60, mask & 0xFF)
		self.top.cmdFPGAWrite(0x61, (mask >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x62, (mask >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x63, (mask >> 24) & 0xFF)
		self.top.cmdFPGAWrite(0x64, (mask >> 32) & 0xFF)
		self.top.cmdFPGAWrite(0x65, (mask >> 40) & 0xFF)

	def setOutputs(self, mask):
		self.desiredOutMask = mask
		self.__updateOut()
		self.top.flushCommands()

	def getInputs(self):
		self.top.cmdFPGARead(0x60)
		self.top.cmdFPGARead(0x61)
		self.top.cmdFPGARead(0x62)
		self.top.cmdFPGARead(0x63)
		self.top.cmdFPGARead(0x64)
		self.top.cmdFPGARead(0x65)
		inputs = self.top.cmdReadBufferReg48()
		return inputs

	def __updateOscDivider(self):
		div = self.oscDiv
		self.top.cmdFPGAWrite(0x00, div & 0xFF)
		self.top.cmdFPGAWrite(0x01, (div >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x02, (div >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x03, (div >> 24) & 0xFF)

	def setOscDivider(self, div):
		self.oscDiv = div
		self.__updateOscDivider()
		self.top.flushCommands()

	def __updateOscMask(self):
		mask = self.oscMask
		mask &= self.getActivePinMask()
		self.top.cmdFPGAWrite(0x20, mask & 0xFF)
		self.top.cmdFPGAWrite(0x21, (mask >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x22, (mask >> 16) & 0xFF)
		self.top.cmdFPGAWrite(0x23, (mask >> 24) & 0xFF)
		self.top.cmdFPGAWrite(0x24, (mask >> 32) & 0xFF)
		self.top.cmdFPGAWrite(0x25, (mask >> 40) & 0xFF)

	def setOscMask(self, mask):
		self.oscMask = mask
		self.__updateOscMask()
		self.__updateOutEn()
		self.__updateOut()
		self.top.flushCommands()

	def __updateFreqCountPin(self):
		if self.mode == self.MODE_FCNT:
			value = self.fcntPin
			self.top.cmdFPGAWrite(0x80, value)

	def setFreqCountPin(self, pinNumber, invert=False):
		assert(pinNumber <= 0x3F)
		value = pinNumber & 0x3F
		if invert:
			value |= 0x80
		self.fcntPin = value
		self.__updateFreqCountPin()
		self.top.flushCommands()

	def getFreqCount(self):
		if self.mode != self.MODE_FCNT:
			return 0
		self.top.cmdFPGARead(0x00)
		self.top.cmdFPGARead(0x01)
		self.top.cmdFPGARead(0x02)
		self.top.cmdFPGARead(0x03)
		count = self.top.cmdReadBufferReg32()
		return count

ChipDescription(
	Chip_Unitest,
	chipID = "unitest",
	bitfile = "unitest",
	runtimeID = (8, 1),
	chipType = ChipDescription.TYPE_INTERNAL,
	description = "Universal device tester",
)
