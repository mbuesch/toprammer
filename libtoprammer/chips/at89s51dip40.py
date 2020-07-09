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


class Chip_AT89S51dip40(Chip):
	STAT_BUSY	= 0x01 # Programmer is running a command
	STAT_ERR	= 0x02 # Error during write

	def __init__(self):
		Chip.__init__(self,
			      chipPackage = "DIP40",
			      chipPinVCC = 40,
			      chipPinsVPP = 31,
			      chipPinGND = 20)
		self.flashPageSize = 0x2000
		self.flashPages = 1

	def __initChip(self):
		self.applyVCC(False)
		self.applyVPP(False)
		self.applyGND(True)
		self.top.cmdSetVCCVoltage(5)
		self.top.cmdSetVPPVoltage(5)

	def readSignature(self):
		self.__initChip()
		self.top.cmdEnableZifPullups(True)
		self.applyGND(True)
		self.applyVCC(True)
		self.top.cmdSetVPPVoltage(5)
		self.__loadCommand(5) # VPP on
		self.applyVPP(True)
		self.__loadCommand(1) # set nPROG
		self.__loadAddress(0x0100)
		self.__setPx()
		data = b""
		self.top.cmdFPGARead(0x10)
		self.__loadAddress(0x0200)
		self.top.cmdFPGARead(0x10)		
		data += self.top.cmdReadBufferReg()
		self.applyVPP(False)
		self.__loadCommand(6) # VPP off
		signature = b""
		signature += int2byte(data[0])
		signature += int2byte(data[1])
		self.top.printInfo("Signature: %X, %X"  % (byte2int(signature[0]), byte2int(signature[1])))
		return signature

	def erase(self):
		self.__initChip()
		self.applyGND(True)
		self.applyVCC(True)
		self.__loadCommand(1) # set P3.2
		self.top.cmdSetVPPVoltage(5)
		self.__loadCommand(5) # VPP on
		self.applyVPP(True)
		self.top.cmdDelay(0.5)
		self.__setPx(P26=1, P33=1)
		self.top.cmdSetVPPVoltage(12)
		self.__runCommandSync(3)
		self.top.cmdDelay(0.5)
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(5)
		self.__setPx()
		self.__loadCommand(6) # VPP off
		self.top.flushCommands()
		self.top.printInfo("{chipid}: Erasing flash, verifying ...".format(chipid=self.chipDescription.chipID))
		ok = self.__verifyErase()
		if ok == 0:
			self.top.printInfo("{chipid}: Erase done.".format(chipid=self.chipDescription.chipID))
		else:
			self.top.printInfo("{chipid}: Erase failed!".format(chipid=self.chipDescription.chipID))

	def readProgmem(self):
		self.__initChip()
		self.top.cmdEnableZifPullups(True)
		self.applyGND(True)
		self.applyVCC(True)
		self.top.cmdSetVPPVoltage(5)
		self.__loadCommand(5) # VPP on
		self.applyVPP(True)
		self.__loadCommand(1) # set nPROG
		self.__setPx(P36=1, P37=1)
		#self.__setPx(P26=1, P27=1, P36=1)
		#self.__setPx()
		image = b""
		byteCount = 0
		self.progressMeterInit("Reading Flash", self.flashPageSize*self.flashPages)
		for addr in range(0, self.flashPageSize*self.flashPages):
			self.progressMeter(addr)
			self.__loadAddress(addr)
			#self.__runCommandSync(4)
			self.top.cmdFPGARead(0x10)
			byteCount += 1
			if byteCount == self.top.getBufferRegSize():
				image += self.top.cmdReadBufferReg(byteCount)
				byteCount = 0
		image += self.top.cmdReadBufferReg(byteCount)
		self.applyVPP(False)
		self.__setPx()
		self.__loadCommand(6) # VPP off
		self.top.flushCommands()
		self.progressMeterFinish()

		return image

	def writeProgmem(self, image):
		if len(image) > self.flashPageSize*self.flashPages:
			self.throwError("Invalid FLASH image size %d (expected <=%d)" %\
				(len(image), self.flashPageSize*self.flashPages))
		self.__initChip()
		self.top.cmdEnableZifPullups(True)
		self.applyGND(True)
		self.applyVCC(True)
		self.__loadCommand(1) # set P3.2
		self.top.cmdSetVPPVoltage(5)
		self.__loadCommand(5) # VPP on
		self.applyVPP(True)
		self.__setPx(P27=1, P33=1, P36=1, P37=1)
		self.top.cmdSetVPPVoltage(12)
		self.progressMeterInit("Writing Flash", len(image))
		for addr in range(0, len(image)):
			self.progressMeter(addr)
			data = byte2int(image[addr])
			if data != 0xFF:
				self.__loadData(data)
				self.__loadAddress(addr)
				self.__loadCommand(3)
				ok = self.__progWait()
				if (ok & self.STAT_ERR) != 0:
					self.throwError("Write byte failed.")
		self.top.flushCommands()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(5)
		self.__setPx()
		self.__loadCommand(6) # VPP off
		self.progressMeterFinish()
		ok = self.__verifyProgmem(image)
		if ok == 0:
			self.top.printInfo("{chipid}: Write flash done.".format(chipid = self.chipDescription.chipID))
		else:
			self.top.printInfo("{chipid}: Write flash failed!".format(chipid = self.chipDescription.chipID))

	def readLockbits(self):
		self.__initChip()
		self.top.cmdEnableZifPullups(True)		
		self.applyGND(True)
		self.applyVCC(True)
		self.top.cmdSetVPPVoltage(5)
		self.__loadCommand(5) # VPP on
		self.applyVPP(True)
		self.__loadCommand(1) # set nPROG
		self.__setPx(P26=1, P27=1, P36=1)
		data = b""
		self.top.cmdFPGARead(0x10)
		data += self.top.cmdReadBufferReg()
		self.applyVPP(False)
		self.__loadCommand(6) # VPP off
		lockbits = b""
		lockbits += int2byte(data[0])
		return lockbits

	def writeLockbits(self, image):
		if len(image) != 1:
			self.throwError("Invalid lock-bits image size %d (expected %d)" %\
				(len(image), 1))
		self.progressMeterInit("Writing lock bits", 3)
		lbMask = 0x04
		lb=byte2int(image[0])
		if(lb & lbMask ):
			self.progressMeter(1)
			self.__writeLockbit(1)
		lbMask <<= 1
		if(lb & lbMask ):
			self.progressMeter(2)
			self.__writeLockbit(2)
		lbMask <<= 1
		if(lb & lbMask ):
			self.progressMeter(3)
			self.__writeLockbit(3)
		self.progressMeterFinish()
	
	def __writeLockbit(self, lb):
		self.__initChip()
		self.applyGND(True)
		self.applyVCC(True)
		self.__loadCommand(1)
		self.top.cmdSetVPPVoltage(5)
		self.__loadCommand(5) # VPP on
		self.applyVPP(True)
		self.top.cmdSetVPPVoltage(12)
		if(lb == 1 ):
			self.__setPx(P26=1, P27=1, P33=1, P36=1, P37=1)
			self.__runCommandSync(3)
		elif(lb == 2 ):
			self.__setPx(P26=1, P27=1, P33=1, P36=0, P37=0)
			self.__runCommandSync(3)
		elif(lb == 3 ):
			self.__setPx(P26=1, P27=0, P33=1, P36=1, P37=0)
			self.__runCommandSync(3)
		self.top.flushCommands()
		self.applyVPP(False)
		self.top.cmdSetVPPVoltage(5)
		self.__setPx()
		self.__loadCommand(6) # VPP off

	def __verifyErase(self):
		ok = 0
		image = self.readProgmem()
		for addr in range(0, self.flashPageSize*self.flashPages):
			if byte2int(image[addr]) != 0xFF:
				ok = 1
		return ok

	def __verifyProgmem(self,image):
		data = self.readProgmem()
		ok = 0
		for addr in range(0, len(image)-1):
			if byte2int(image[addr]) != byte2int(data[addr]):
				ok = 1
		return ok

	def __loadData(self, data):
		self.top.cmdFPGAWrite(0x10, data)
		
	def __loadAddress(self, addr):
		self.top.cmdFPGAWrite(0x11, addr & 0x00FF)
		self.top.cmdFPGAWrite(0x12, (addr >> 8) & 0x3FFF)		

	def __loadCommand(self, command):
		self.top.cmdFPGAWrite(0x13, command & 0xFF)

	def __runCommandSync(self, command):
		self.__loadCommand(command)
		self.__busyWait()

	def __setPx(self, P26=0, P27=0, P33=0, P36=0, P37=0, nPSEN=0, RST=1):
		data = 0
		if P26:
			data |= 1
		if P27:
			data |= 2
		if P33:
			data |= 4
		if P36:
			data |= 8
		if P37:
			data |= 16
		if nPSEN:
			data |= 32
		if RST:
			data |= 64
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
lockbitDesc = (
	BitDescription(0, "Unused"),
	BitDescription(1, "Unused"),
	BitDescription(2, "BLB01 - further programming of flash mem. is disabled"),
	BitDescription(3, "BLB02 - verify disabled"),
	BitDescription(4, "BLB03 - external execution disabled"),
	BitDescription(5, "Unused"),
	BitDescription(6, "Unused"),
	BitDescription(7, "Unused"),
	BitDescription(8, "Unused"),
)

ChipDescription(
	Chip_AT89S51dip40,
	bitfile = "at89s5xdip40",
	chipID = "at89s51dip40",	
	runtimeID = (0x0005, 0x01),
	chipVendors = "Atmel",
	description = "AT89S51",
	lockbitDesc = lockbitDesc,
	maintainer = None,
	packages = ( ("DIP40", ""), )
)
