"""
#    TOP2049 Open Source programming suite
#
#    Microchip8 - 18f97j60 family - 8bit PIC MCU
#
#    Copyright (c) 2013 Pavel Stemberk <stemberk@gmail.com>
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

from libtoprammer.chips.microchip8.microchip8_18_common import *

class microchip8_18f97j60family(Chip_Microchip8_18_common):
	
	voltageVDD				 = 3
	voltageVPP				 = 3
	
	delayP5A = 0.000000040  # Delay between 4-bit command operand and next 4-bit command
	delayP9 = 0.0034  # SCK High time (minimum programming time)
	delayP10 = 0.000005  # SCK Low time after programming (high-voltage discharge time)
	delayP11 = 0.475  # Delay to allow self-timed data write or bulk erase to occur
	delayP12 = 0.0004  # Input data hold time from nMCLR/Vpp rise
	delayP19 = 0.000001 # Delay from first nMCLR fall to first PGC rise for key sequence on PGD
	delayP20 = 0.00000004 # Delay from last PGC fall for key sequence on PGD to second nMCLR rise
	
	def __init__(self,
			chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
			signature,
			flashPageSize, flashPages,
			eepromPageSize, eepromPages,
			fuseBytes
			):
		Chip_Microchip8_18_common.__init__(self,
		chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
			signature,
			flashPageSize, flashPages,
			eepromPageSize, eepromPages,
			fuseBytes)
		
	def enterPM(self, force=False):
		if self.isInPmMode and not force:
			return
		"Enter HV programming mode. Vdd first entry mode"
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(False)
		self.setPins(0, 0)
		#self.top.cmdSetVCCVoltage(self.voltageVDD)
		self.top.cmdSetVPPVoltage(self.voltageVPP)
		self.applyGND(True)
		self.applyVCC(True)
		self.top.hostDelay(self.delayP13)
		self.applyVPP(True)
		self.applyVPP(False)
		self.top.hostDelay(self.delayP19)
		self.setTopProgrammerDelays()
		#program entry code
		#print("sending enterpm")
		self.top.cmdFPGAWrite(0x18,0xFF)
		self.top.hostDelay(self.delayP20)
		self.applyVPP(True)
		self.top.hostDelay(self.delayP12)
		
		self.isInPmMode = True
		
	def erase(self):
		self.progressMeterInit("Erasing chip", 0)
		self.enterPM(True)
		self.executeCode(self.getCodeAddrToTBLPTR(0x3C0004))
		self.send4bitWriteInstruction(self.CMD_TW, 0x0080)
		self.executeCode((0x0000,))
		self.sendCommand(1)		
		self.top.hostDelay(self.delayP11 + self.delayP10)
		for i in range(0,4):
			self.sendCommand(1)
		self.top.flushCommands()
		self.progressMeterFinish()

	def writeSequentialBlock(self, startAddr, image, size, infoText):
		if len(image) > size:
			self.throwError("Invalid flash image size %d (expected <=%d)" % \
				(len(image), self.userIDLocationSize))
		self.enterPM()
		self.executeCode((0x8EA6, 0x9CA6))
		self.progressMeterInit(infoText, len(image) // 8)
		self.executeCode(self.getCodeAddrToTBLPTR(startAddr))
		for blockAddr in range(0, len(image), 8):
			self.write8bytes(image[blockAddr:])
			self.progressMeter(blockAddr)
		self.progressMeterFinish()
		self.exitPM()
