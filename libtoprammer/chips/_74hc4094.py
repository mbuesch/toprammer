"""
#    TOP2049 Open Source programming suite
#
#    74HC4094 unit-tester
#
#    Copyright (c) 2011 Michael Buesch <m@bues.ch>
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

from .unitest import *

class Chip_74hc4094(Chip_Unitest):
	def __init__(self):
		Chip_Unitest.__init__(self, chipPackage="DIP16",
					    chipPinVCC=16,
					    chipPinGND=8,
					    VCCVoltage=5)

	def __initChip(self):
		self.zifPin_STR = self.generator.getZifPinForPackagePin(1)
		self.zifPin_D = self.generator.getZifPinForPackagePin(2)
		self.zifPin_CP = self.generator.getZifPinForPackagePin(3)
		self.zifPin_OE = self.generator.getZifPinForPackagePin(15)
		self.zifPin_QS1 = self.generator.getZifPinForPackagePin(9)
		self.zifPin_QS2 = self.generator.getZifPinForPackagePin(10)
		self.zifPins_QP = []
		for packagePin in (4, 5, 6, 7, 14, 13, 12, 11):
			self.zifPins_QP.append(
				self.generator.getZifPinForPackagePin(packagePin))

		self.reset()

		outen = 0
		for zifPin in (self.zifPin_STR, self.zifPin_D,
			       self.zifPin_CP, self.zifPin_OE):
			outen |= (1 << (zifPin - 1))
		self.setOutputEnableMask(outen)

		self.applyGND(True)
		self.applyVCC(True)

	def test(self):
		testPatterns = (0xFF, 0x00, 0xAA, 0x55, 0xF0, 0x0F,
				0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,
				0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01, 0x00)

		self.progressMeterInit("Logic test", len(testPatterns))
		self.__initChip()

		# Initialize the register to all-zero
		self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=0, OE=0))
		for i in range(0, 9):
			self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=1, OE=0))
			self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=0, OE=0))
		self.setOutputs(self.__makeOutMask(STR=1, D=0, CP=0, OE=0))
		self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=0, OE=1))

		QP = self.__readQP()
		if QP != 0x00:
			self.throwError("Failed to clear the shiftregister. Got 0x%02X" % QP)

		prevContents = 0x00
		prev_QS1 = False
		count = 0
		for testPattern in testPatterns:
			self.progressMeter(count)
			self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=0, OE=0))
			for bitNr in range(7, -1, -1): # MSB first
				self.setOutputs(self.__makeOutMask(STR=0,
								   D=(testPattern & (1 << bitNr)),
								   CP=0, OE=0))
				self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=1, OE=0))
				(QS1, QS2) = self.__readQS()
				word = (prevContents << 8) | testPattern
				expect_QS1 = bool(word & (1 << (bitNr + 7)))
				expect_QS2 = prev_QS1
				prev_QS1 = expect_QS1
				if QS1 != expect_QS1 or QS2 != expect_QS2:
					self.throwError("Got invalid QS serial output for "
						"test pattern 0x%02X bit %d. Got %d/%d, but "
						"expected %d/%d" %\
						(testPattern, bitNr, QS1, QS2,
						 expect_QS1, expect_QS2))
				self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=0, OE=0))
			self.setOutputs(self.__makeOutMask(STR=1, D=0, CP=0, OE=0))
			self.setOutputs(self.__makeOutMask(STR=0, D=0, CP=0, OE=1))

			QP = self.__readQP()
			if QP != testPattern:
				self.throwError("Failed on test pattern 0x%02X. Got 0x%02X" %\
						(testPattern, QP))

			prevContents = testPattern
			count += 1
		self.progressMeterFinish()

	def __makeOutMask(self, STR, D, CP, OE):
		mask = 0
		if STR:
			mask |= (1 << (self.zifPin_STR - 1))
		if D:
			mask |= (1 << (self.zifPin_D - 1))
		if CP:
			mask |= (1 << (self.zifPin_CP - 1))
		if OE:
			mask |= (1 << (self.zifPin_OE - 1))
		return mask

	def __readQP(self):
		QPValue = 0
		count = 0
		inputs = self.getInputs()
		for zifPin in self.zifPins_QP:
			if inputs & (1 << (zifPin - 1)):
				QPValue |= (1 << count)
			count += 1
		return QPValue

	def __readQS(self):
		QS1 = False
		QS2 = False
		inputs = self.getInputs()
		if inputs & (1 << (self.zifPin_QS1 - 1)):
			QS1 = True
		if inputs & (1 << (self.zifPin_QS2 - 1)):
			QS2 = True
		return (QS1, QS2)

ChipDescription(
	Chip_74hc4094,
	chipID = "74hc4094dip16",
	bitfile = "unitest",
	runtimeID = (0x0008, 0x01),
	chipType = ChipDescription.TYPE_LOGIC,
	description = "74HC(T)4094 shift-register",
	chipVendors = ("Philips", "Other"),
)
