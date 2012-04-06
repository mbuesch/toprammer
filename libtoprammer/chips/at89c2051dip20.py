"""
#    TOP2049 Open Source programming suite
#
#    Atmel AT89C2051 DIP20 Support
#
#    Copyright (c) 2010 Guido
#    Copyright (c) 2010 Michael Buesch <m@bues.ch>
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


class Chip_AT89C2051dip20(Chip):
	STAT_BUSY	= 0x01 # Programmer is running a command
	STAT_ERR	= 0x02 # Error during write

	def __init__(self):
		Chip.__init__(self,
			      chipPackage = "DIP20",
			      chipPinVCC = 20,
			      chipPinsVPP = 1,
			      chipPinGND = 10)

	def __initChip(self):
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(True)
		self.top.cmdSetVCCVoltage(5)
		self.top.cmdSetVPPVoltage(5)

	def readSignature(self):
		self.__initChip()
		self.applyGND(True)
		self.applyVCC(True)
		self.top.cmdSetVPPVoltage(5)
		self.__loadCommand(5) # VPP on
		self.__loadCommand(1) # set P3.2
		self.__setP3x(P33=0, P34=0, P35=0, IA=0)
		data = ""
		self.top.cmdFPGARead(0x10)
		self.__setP3x(P33=0, P34=0, P35=0, IA=1)
		self.__setP3x(P33=0, P34=0, P35=0, IA=0)
		self.top.cmdFPGARead(0x10)
		self.__setP3x(P33=0, P34=0, P35=0, IA=1)
		self.__setP3x(P33=0, P34=0, P35=0, IA=0)
		self.top.cmdFPGARead(0x10)
		data += self.top.cmdReadBufferReg()
		self.__setP3x(P33=0, P34=1, P35=0, IA=0)
		self.__loadCommand(6) # VPP off
		signature = ""
		signature += data[0]
		signature += data[1]
		self.top.printInfo("Signature: %X, %X"  % (byte2int(signature[0]), byte2int(signature[1])))
		return signature

	def erase(self):
		self.__initChip()
		self.applyGND(True)
		self.applyVCC(True)
		self.__loadCommand(1) # set P3.2
		self.top.cmdSetVPPVoltage(5)
		self.applyVPP(True)
		self.__loadCommand(5) # VPP on
		self.__setP3x(P33=1, P34=0, P35=0, IA=0)
		self.top.cmdSetVPPVoltage(12)
		self.__runCommandSync(4)
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(5)
		self.__setP3x(P33=0, P34=1, P35=0, IA=0)
		self.__loadCommand(5) # VPP off
		self.top.flushCommands()
		self.top.printInfo("at89c2051dip20: Erasing flash, verifying ...")
		ok = self.__verifyErase()
		if ok == 0:
			self.top.printInfo("at89c2051dip20: Erase done.")
		else:
			self.top.printInfo("at89c2051dip20: Erase failed!")

	def readProgmem(self):
		self.__initChip()
		self.applyGND(True)
		self.applyVCC(True)
		self.__loadCommand(1) # set P3.2
		self.top.cmdSetVPPVoltage(5)
		self.applyVPP(True)
		self.__loadCommand(5) # VPP on
		self.__setP3x(P33=0, P34=0, P35=1, IA=0)
		image = ""
		byteCount = 0
		self.progressMeterInit("Reading Flash", 0x800)
		for addr in range(0, 0x800):
			self.progressMeter(addr)
			self.top.cmdFPGARead(0x10)
			self.__setP3x(P33=0, P34=0, P35=1, IA=1)
			self.__setP3x(P33=0, P34=0, P35=1, IA=0)
			byteCount += 1
			if byteCount == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(byteCount)
				byteCount = 0
		image += self.top.cmdReadBufferReg(byteCount)
		self.applyVPP(False)
		self.__setP3x(P33=0, P34=1, P35=0, IA=0)
		self.__loadCommand(5) # VPP off
		self.top.flushCommands()
		self.progressMeterFinish()

		return image

	def writeProgmem(self, image):
		if len(image) > 0x800:
			self.throwError("Invalid EPROM image size %d (expected <=%d)" %\
				(len(image), 0x800))
		self.__initChip()
		self.applyGND(True)
		self.applyVCC(True)
		self.__loadCommand(1) # set P3.2
		self.top.cmdSetVPPVoltage(5)
		self.applyVPP(True)
		self.__loadCommand(5) # VPP on
		self.__setP3x(P33=0, P34=1, P35=1, IA=0)
		self.top.cmdSetVPPVoltage(12)
		self.progressMeterInit("Writing Flash", len(image))
		for addr in range(0, len(image)):
			self.progressMeter(addr)
			data = byte2int(image[addr])
			if data != 0xFF:
				self.__loadData(data)
				self.__loadCommand(3)
				ok = self.__progWait()
				if (ok & self.STAT_ERR) != 0:
					self.throwError("Write byte failed.")
			self.__setP3x(P33=0, P34=1, P35=1, IA=1)
			self.__setP3x(P33=0, P34=1, P35=1, IA=0)
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(5)
		self.__setP3x(P33=0, P34=1, P35=0, IA=0)
		self.__loadCommand(5) # VPP off
		self.top.flushCommands()
		self.progressMeterFinish()
		ok = self.__verifyProgmem(image)
		if ok == 0:
			self.top.printInfo("at89c2051dip20: Write flash done.")
		else:
			self.top.printInfo("at89c2051dip20: Write flash failed!")

	def __verifyErase(self):
		ok = 0
		image = self.readProgmem()
		for addr in range(0, 0x800):
			if byte2int(image[addr]) != 0xFF:
				ok = 1
		return ok

	def __verifyProgmem(self,image):
		data = self.readProgmem()
		ok = 0
		for addr in range(0, 0x800):
			if byte2int(image[addr]) != byte2int(data[addr]):
				ok = 1
		return ok

	def __loadData(self, data):
		self.top.cmdFPGAWrite(0x10, data)

	def __loadCommand(self, command):
		self.top.cmdFPGAWrite(0x12, command & 0xFF)

	def __runCommandSync(self, command):
		self.__loadCommand(command)
		self.__busyWait()

	def __setP3x(self, P33, P34, P35, IA):
		data = 0
		if P33:
			data |= 1
		if P34:
			data |= 2
		if P35:
			data |= 4
		if IA:
			data |= 8
		self.top.cmdFPGAWrite(0x16, data)

	def __getStatusFlags(self):
		self.top.cmdFPGARead(0x12)
		stat = self.top.cmdReadBufferReg()
		return byte2int(stat[0])

	def __busy(self):
		return bool(self.__getStatusFlags() & self.STAT_BUSY)

	def __busyWait(self):
		for i in range(0, 26):
			if not self.__busy():
				return
			self.top.hostDelay(0.001)
		self.throwError("Timeout in busywait.")

	def __progWait(self):
		for i in range(0,4):
			self.top.cmdFPGARead(0x12)
			stat = self.top.cmdReadBufferReg()
			if (byte2int(stat[0]) & self.STAT_BUSY) == 0:
				return byte2int(stat[0])
			self.top.hostDelay(0.001)
		self.throwError("Timeout in busywait.")

ChipDescription(
	Chip_AT89C2051dip20,
	bitfile = "at89c2051dip20",
	runtimeID = (0x0005, 0x01),
	chipVendors = "Atmel",
	description = "AT89C2051",
	maintainer = None,
	packages = ( ("DIP20", ""), )
)
