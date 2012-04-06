"""
#    TOP2049 Open Source programming suite
#
#    Cypress M8C In System Serial Programmer
#
#    Copyright (c) 2010-2011 Michael Buesch <m@bues.ch>
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
import time


class Chip_M8C_ISSP(Chip):
	ISSPCMD_POR	= 1 # Perform a power-on-reset
	ISSPCMD_PWROFF	= 2 # Turn power off
	ISSPCMD_EXEC	= 3 # Do an "execute" transfer

	STAT_BUSY0		= 0x01
	STAT_BUSY1		= 0x02
	STAT_ISSPSTATE		= 0x1C
	STAT_ISSPSTATE_SHIFT	= 2
	STAT_SDATA		= 0x20

	STRVEC_INIT1 = (
		"1100101010000000000111",
		"0000000000000000000000",
		"0000000000000000000000",
		"0000000000000000000000",
		"0000000000000000000000",
		"0000000000000000000000",
		"1101111011100010000111",
		"1101111101000000000111",
		"1101111011100000000111",
		"1101111011100010000111",
		"1101111111000000100111",
		"1101110001000000100111",
		"1101110000000000011111",
		"1101111011100000000111",
		"1001111100000111010111",
		"1001111100100000011111",
		"1001111101101000000111",
		"1001111110000000000111",
		"1001111111001010110111",
		"1001111110100000001111",
		"1001111111100000001111",
		"1001111111110000000111",
		"1101111011100010000111",
		"1101110001000000000111",
		"1101111111000000000111",
		"1101110000000000000111",
		"1101111011100000000111",
		"1101111010000000011111",
		"1101111010100000000111",
		"1101111011000000000111",
		"1101111100000000000111",
		"1101111100100110000111",
	)

	STRVEC_INIT2 = (
		"1001111101000000000111",
		"1101111000000000110111",
		"1101111100000000000111",
		"1101111111100010010111",
	)

	STRVEC_IDSETUP = (
		"1101111011100010000111",
		"1101110000000000010111",
		"1101111011100010000111",
		"1101111101000000000111",
		"1101111011100000000111",
		"1101111011100010000111",
		"1101111111000000100111",
		"1101110001000000100111",
		"1101110000000000011111",
		"1101111011100000000111",
		"1001111100000111010111",
		"1001111100100000011111",
		"1001111101101000000111",
		"1001111110000000000111",
		"1001111111001010110111",
		"1001111110100000001111",
		"1001111111100000001111",
		"1001111111110000000111",
		"1101111011100010000111",
		"1101110001000000000111",
		"1101111111000000000111",
		"1101110000000000000111",
		"1101111011100000000111",
		"1101111010000000011111",
		"1101111010100000000111",
		"1101111011000000000111",
		"1101111100000000000111",
		"1101111100100110000111",
		"1001111101000000000111",
		"1101111000000000110111",
		"1101111100000000000111",
		"1101111111100010010111",
	)

	STRVEC_READBYTE = (
		"101aaaaaaaaZDDDDDDDDZ1",
	)

	STRVEC_WRITEBYTE = (
		"100aaaaaaaadddddddd111",
	)

	STRVEC_ERASEALL = (
		"1001111110000010101111",
		"1001111111001010110111",
		"1101111011100010000111",
		"1101111101000000000111",
		"1101111011100000000111",
		"1101111011100010000111",
		"1101111111000000100111",
		"1101110001000000100111",
		"1101110000000000011111",
		"1101111011100000000111",
		"1001111100000111010111",
		"1001111100100000011111",
		"1001111101101000000111",
		"1001111110000000000111",
		"1001111111001010110111",
		"1001111110100000001111",
		"1001111111100000001111",
		"1001111111110000000111",
		"1101111011100010000111",
		"1101110001000000000111",
		"1101111111000000000111",
		"1101110000000000000111",
		"1101111011100000000111",
		"1101111010000000011111",
		"1101111010100000000111",
		"1101111011000000000111",
		"1101111100000000000111",
		"1101111100100110000111",
		"1101111000000000101111",
		"1101111100000000000111",
		"1101111111100010010111",
	)

	STRVEC_SETBLKNUM = (
		"10011111010dddddddd111",
	)

	STRVEC_READBLK = (
		"1101111011100010000111",
		"1101111101000000000111",
		"1101111011100000000111",
		"1101111011100010000111",
		"1101111111000000100111",
		"1101110001000000100111",
		"1101110000000000011111",
		"1101111011100000000111",
		"1001111100000111010111",
		"1001111100100000011111",
		"1001111101101000000111",
		"1001111110000000000111",
		"1001111111001010110111",
		"1001111110100000001111",
		"1001111111100000001111",
		"1001111111110000000111",
		"1101111011100010000111",
		"1101110001000000000111",
		"1101111111000000000111",
		"1101110000000000000111",
		"1101111011100000000111",
		"1101111010000000011111",
		"1101111010100000000111",
		"1101111011000000000111",
		"1101111100000000000111",
		"1101111100100110000111",
		"1101111000000000001111",
		"1101111100000000000111",
		"1101111111100010010111",
	)

	STRVEC_WRITEBLK = (
		"1001111110001010100111",
		"1001111111001010110111",
		"1101111011100010000111",
		"1101111101000000000111",
		"1101111011100000000111",
		"1101111011100010000111",
		"1101111111000000100111",
		"1101110001000000100111",
		"1101110000000000011111",
		"1101111011100000000111",
		"1001111100000111010111",
		"1001111100100000011111",
		"1001111101101000000111",
		"1001111110000000000111",
		"1001111111001010110111",
		"1001111110100000001111",
		"1001111111100000001111",
		"1001111111110000000111",
		"1101111011100010000111",
		"1101110001000000000111",
		"1101111111000000000111",
		"1101110000000000000111",
		"1101111011100000000111",
		"1101111010000000011111",
		"1101111010100000000111",
		"1101111011000000000111",
		"1101111100000000000111",
		"1101111100100110000111",
		"1101111000000000010111",
		"1101111100000000000111",
		"1101111111100010010111",
	)

	STRVEC_READCHKSUM = (
		"10111111001ZDDDDDDDDZ1",
		"10111111000ZDDDDDDDDZ1",
	)

	STRVEC_READID = (
		"10111111000ZDDDDDDDDZ1",
		"10111111001ZDDDDDDDDZ1",
	)

	def __init__(self):
		Chip.__init__(self)
#		self.progmemSize = 1024 * 16
		self.progmemSize = 256#XXX

	def readSignature(self):
		self.progressMeterInit("Reading chip ID", 0)
		self.__powerOnReset()
		gotID = self.__readID()
		self.progressMeterFinish()

		return int2byte(gotID & 0xFF) + int2byte((gotID >> 8) & 0xFF)

	def erase(self):
		self.progressMeterInit("Erasing chip", 0)
		self.__powerOnReset()
		self.__bitbangStringVectors(self.STRVEC_ERASEALL)
		self.__runCommandSync(self.ISSPCMD_EXEC)
		self.progressMeterFinish()

	def writeProgmem(self, image):
		if len(image) > self.progmemSize or len(image) % 64 != 0:
			self.throwError("Invalid program memory image size %d "
					"(expected <=%d and multiple of 64)" %\
				(len(image), self.progmemSize))

		self.progressMeterInit("Writing program memory", len(image))
		self.__powerOnReset()
		for blknum in range(0, len(image) // 64):
			for i in range(0, 64):
				self.progressMeter(blknum * 64 + i)
				self.__writeByte(i, byte2int(image[blknum * 64 + i]))
			vec = self.__stringVectorReplace(self.STRVEC_SETBLKNUM[0], "d", blknum)
			self.__bitbangStringVector(vec)
			self.__bitbangStringVectors(self.STRVEC_WRITEBLK)
			self.__runCommandSync(self.ISSPCMD_EXEC)
		self.progressMeterFinish()

	def readProgmem(self):
		self.progressMeterInit("Reading program memory", self.progmemSize)
		self.__powerOnReset()
		assert(self.progmemSize % 64 == 0)
		image = []
		for blknum in range(0, self.progmemSize // 64):
			vec = self.__stringVectorReplace(self.STRVEC_SETBLKNUM[0], "d", blknum)
			self.__bitbangStringVector(vec)
			self.__bitbangStringVectors(self.STRVEC_READBLK)
			self.__runCommandSync(self.ISSPCMD_EXEC)
			for i in range(0, 64):
				self.progressMeter(blknum * 64 + i)
				image.append(int2byte(self.__readByte(i)))
			#FIXME return_code
		self.progressMeterFinish()
		return b"".join(image)

	def __powerDown(self):
		"Turn the power to the device off"
		self.printDebug("Powering device down...")
		self.__runCommandSync(self.ISSPCMD_PWROFF)
		self.top.hostDelay(5)

	def __powerOnReset(self):
		"Perform a complete power-on-reset and initialization"
		self.top.vcc.setLayoutMask(0)
		self.top.vpp.setLayoutMask(0)
		self.top.gnd.setLayoutMask(0)
		self.top.cmdSetVCCVoltage(5)
		self.top.cmdSetVPPVoltage(5)

		self.printDebug("Initializing supply power...")
		self.top.gnd.setLayoutPins( (20,) )
		self.top.vcc.setLayoutPins( (21,) )

#FIXME when to do exec?
		self.__powerDown()
		self.printDebug("Performing a power-on-reset...")
		self.__uploadStringVector(self.STRVEC_INIT1[0])
		self.__runCommandSync(self.ISSPCMD_POR)
		self.printDebug("Sending vector 1...")
		self.__bitbangStringVectors(self.STRVEC_INIT1[1:])
#XXX		self.__runCommandSync(self.ISSPCMD_EXEC)
		self.printDebug("Sending vector 2...")
		self.__bitbangStringVectors(self.STRVEC_INIT2)
		self.__runCommandSync(self.ISSPCMD_EXEC)

	def __readID(self):
		"Read the silicon ID"
		self.__bitbangStringVectors(self.STRVEC_IDSETUP)
		self.__runCommandSync(self.ISSPCMD_EXEC)

		low = (self.__bitbangStringVector(self.STRVEC_READID[0]) >> 2) & 0xFF
		high = (self.__bitbangStringVector(self.STRVEC_READID[1]) >> 2) & 0xFF

		return low | (high << 8)

	def __readByte(self, address):
		vec = self.__stringVectorReplace(self.STRVEC_READBYTE[0], "a", address)
		inputData = self.__bitbangStringVector(vec)
		return (inputData >> 2) & 0xFF

	def __writeByte(self, address, byte):
		vec = self.__stringVectorReplace(self.STRVEC_WRITEBYTE[0], "a", address)
		vec = self.__stringVectorReplace(vec, "d", byte)
		self.__bitbangStringVector(vec)

	def __loadCommand(self, command):
		self.top.cmdFPGAWrite(0x11, command & 0xFF)

	def __runCommandSync(self, command):
		self.printDebug("Running synchronous command %d" % command)
		self.__loadCommand(command)
		self.__busyWait()

	def __setBitbang(self, SDATA, SDATA_in, SCLK, SCLK_z):
		value = 0
		if SDATA:
			value |= 0x01
		if SDATA_in:
			value |= 0x02
		if SCLK:
			value |= 0x04
		if SCLK_z:
			value |= 0x08
		self.top.cmdFPGAWrite(0x10, value)

	def __getStatusFlags(self):
		self.top.cmdFPGARead(0x10)
		stat = self.top.cmdReadBufferReg8()
		isspState = (stat & self.STAT_ISSPSTATE) >> self.STAT_ISSPSTATE_SHIFT
		sdata = bool(stat & self.STAT_SDATA)
		isBusy = bool(stat & self.STAT_BUSY0) != bool(stat & self.STAT_BUSY1)
		self.printDebug("isspState = 0x%02X, isBusy = %d, busyFlags = 0x%01X, sdata = %d" %\
			(isspState, isBusy, (stat & (self.STAT_BUSY0 | self.STAT_BUSY1)), sdata))
		return (isBusy, sdata, isspState)

	def __busy(self):
		(isBusy, sdata, isspState) = self.__getStatusFlags()
		return isBusy

	def __getSDATA(self):
		(isBusy, sdata, isspState) = self.__getStatusFlags()
		return int(sdata)

	def __busyWait(self):
		for i in range(0, 200):
			if not self.__busy():
				return
			self.top.hostDelay(0.01)
		self.throwError("Timeout in busywait. Chip not responding?")

	def __stringVectorToBinary(self, vector):
		binary = 0
		inputMask = 0
		assert(len(vector) == 22)
		bit = len(vector) - 1
		for b in vector:
			if b == "1":
				binary |= (1 << bit)
			elif b == "0":
				pass
			elif b == "H" or b == "L" or b == "Z" or b == "D":
				inputMask |= (1 << bit)
			else:
				assert(0)
			bit -= 1
		return (binary, inputMask)

	def __stringVectorReplace(self, strVec, replace, data):
		ret = ""
		for i in range(len(strVec) - 1, -1, -1):
			b = strVec[i]
			if b == replace:
				if (data & 1):
					ret = "1" + ret
				else:
					ret = "0" + ret
				data >>= 1
			else:
				ret = b + ret
		return ret

	def __bitbangStringVector(self, strVec):
		vectorSize = len(strVec)
		(vector, inputMask) = self.__stringVectorToBinary(strVec)
		inputData = 0
		self.__setBitbang(SDATA=0, SDATA_in=1, SCLK=0, SCLK_z=0)
		for i in range(vectorSize - 1, -1, -1):
			if inputMask & (1 << i):
				self.__setBitbang(SDATA=0, SDATA_in=1, SCLK=1, SCLK_z=0)
				self.__setBitbang(SDATA=0, SDATA_in=1, SCLK=0, SCLK_z=0)
				self.top.cmdDelay(0.000001)
				sdata = self.__getSDATA()
				inputData |= (sdata << i)
			else:
				self.__setBitbang(SDATA=(vector & (1 << i)), SDATA_in=0,
						  SCLK=1, SCLK_z=0)
				self.__setBitbang(SDATA=0, SDATA_in=0, SCLK=0, SCLK_z=0)
				self.top.cmdDelay(0.000001)
		return inputData

	def __bitbangStringVectors(self, strVecList):
		for strVec in strVecList:
			self.__bitbangStringVector(strVec)

	def __uploadStringVector(self, strVec):
		(vector, inputMask) = self.__stringVectorToBinary(strVec)
		assert(inputMask == 0)
		self.top.cmdFPGAWrite(0x12, vector & 0xFF)
		self.top.cmdFPGAWrite(0x13, (vector >> 8) & 0xFF)
		self.top.cmdFPGAWrite(0x14, (vector >> 8) & 0xFF)

ChipDescription(
	Chip_M8C_ISSP,
	bitfile = "m8c-issp",
	runtimeID = (0x0007, 0x01),
	chipVendors = "Cypress",
	description = "M8C In System Serial Programmer",
	packages = ( ("M8C ISSP header", "Special adapter"), ),
	comment = "Special adapter required",
	broken = True
)
