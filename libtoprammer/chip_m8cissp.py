"""
#    TOP2049 Open Source programming suite
#
#    Cypress M8C In System Serial Programmer
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
import time


class Chip_M8C_ISSP(Chip):
	ISSPCMD_POR	= 1 # Perform a power-on-reset
	ISSPCMD_PWROFF	= 2 # Turn power off
	ISSPCMD_SENDVEC	= 3 # Send a vector
	ISSPCMD_EXEC	= 4 # Do an "execute" transfer

	STAT_BUSY	= 0x01 # Programmer is running a command

	STRVEC_SETFREQ = {
		2	: "1001111110000000101000",
		3	: "1001111110000001001000",
		3.578	: "1001111110000001011000",
		4	: "1001111110000001101000",
		5	: "1001111110000010001000",
		6	: "1001111110000010101000",
		6.66666	: "1001111110000010111000",
		7	: "1001111110000011001000",
		8	: "1001111110000011100000",
		9	: "1001111110000100000000",
		10	: "1001111110000100100000",
		11	: "1001111110000101000000",
		12	: "1001111110000101100000",
	}
	STRVEC_INIT1 = (
		"1100101000000000000000",
		"0000000000000000000000",
		"0000000000000000000000",
		"1000111101100100000000",
		"1101111011100000000000",
		"1101111011000001000000",
		"1001111100000111010000",
		"1001111100100001011000",
		"1101111010100000000000",
		"1101111010000000011000",
		"1001111101100100000000",
		"1101111100100110000000",
		"1101111101001000000000",
		"1101111000000001000000",
		"1101111100000000000000",
		"1101111111100010010000",
	)
	STRVEC_INIT2 = (
		"1101111011100000000000",
		"1101111011000001000000",
		"1001111100000111010000",
		"1001111100100001011000",
		"1101111010100000000000",
		"1101111010000000011000",
		"1001111101100100000000",
		"1101111100100110000000",
		"1101111101001000000000",
		"1001111101000000001000",
		"1101111000000000110000",
		"1101111100000000000000",
		"1101111111100010010000",
	)
	STRVEC_INIT3_HIVDD = (
		"1101111011100000000000",
		"1101111010000000011000",
		"1101111010100000000000",
		"1101111011000001000000",
		"1101111100001010001000",
		"1101111100111111100000",
		"1101111101000110000000",
		"1101111111100010010000",
		"0000000000000000000000",
		"1101111011100000000000",
		"1101111010000000011000",
		"1101111010100000000000",
		"1101111011000001000000",
		"1101111100001100000000",
		"1101111100111101010000",
		"1101111101000110000000",
		"1101111011100010000000",
		"1101111111100010010000",
		"0000000000000000000000",
	)
	STRVEC_INIT3_LOVDD = (
		"1101111011100000000000",
		"1101111010000000011000",
		"1101111010100000000000",
		"1101111011000001000000",
		"1101111100001010001000",
		"1101111100111111000000",
		"1101111101000110000000",
		"1101111111100010010000",
		"0000000000000000000000",
		"1101111011100000000000",
		"1101111010000000011000",
		"1101111010100000000000",
		"1101111011000001000000",
		"1101111100001100000000",
		"1101111100111101010000",
		"1101111101000110000000",
		"1101111011100010000000",
		"1101111111100010010000",
		"0000000000000000000000",
	)
	STRVEC_IDSETUP = (
		"1101111011100000000000",
		"1101111011000001000000",
		"1001111100000111010000",
		"1001111100100001011000",
		"1101111010100000000000",
		"1101111010000000011000",
		"1001111101100100000000",
		"1101111100100110000000",
		"1101111101001000000000",
		"1001111101000000000000",
		"1101111000000000110000",
		"1101111100000000000000",
		"1101111111100010010000",
	)
	STRVEC_READBYTE = "101aaaaaaaaZDDDDDDDDZ0"
	STRVEC_ERASEALL = (
		"1101111011100000000000",
		"1101111011001000000000",
		"1001111100000111010000",
		"1001111100101000011000",
		"1101111010100000000000",
		"1101111010000000011000",
		"1001111101110000000000",
		"1101111100100110000000",
		"1101111101001000000000",
		"1101111000000000101000",
		"1101111100000000000000",
		"1101111111100010010000",
	)
	STRVEC_SECURE = (
		"1101111011100000000000",
		"1101111011001000000000",
		"1001111100000111010000",
		"1001111100101000011000",
		"1101111010100000000000",
		"1101111010000000011000",
		"1001111101110000000000",
		"1101111100100110000000",
		"1101111101001000000000",
		"1101111000000000100000",
		"1101111100000000000000",
		"1101111111100010010000",
	)

	def __init__(self):
		Chip.__init__(self)

	def initializeChip(self):
		self.printDebug("Initializing chip")
		self.top.vccx.setLayoutMask(0)
		self.top.vpp.setLayoutMask(0)
		self.top.gnd.setLayoutPins( [] )
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(5)

		#XXX
		self.__powerOnReset()
		id = self.__readID()
		print "ID=0x%04X" % id

	def shutdownChip(self):
		self.printDebug("Shutdown chip")
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdFlush()
		self.top.cmdSetVPPVoltage(5)
		self.top.cmdFlush()
		self.top.vccx.setLayoutMask(0)
		self.top.vpp.setLayoutMask(0)
		self.top.cmdFlush()
		self.top.gnd.setLayoutPins( [] )

	def __powerDown(self):
		"Turn the power to the device off"
		self.printDebug("Powering device down...")
		self.__runCommandSync(self.ISSPCMD_PWROFF)
		self.top.flushCommands()
		time.sleep(3)

	def __powerOnReset(self):
		"Perform a complete power-on-reset and initialization"
		self.printDebug("Initializing supply power...")
		self.top.gnd.setLayoutPins( (20,) )
		self.top.cmdFlush()
		self.top.vccx.setLayoutPins( (21,) )
		self.top.cmdFlush()
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdFlush()

		self.__powerDown()
		self.printDebug("Performing a power-on-reset...")
		self.__loadStringVector(self.STRVEC_INIT1[0])
		self.__runCommandSync(self.ISSPCMD_POR)
		self.printDebug("Sending vector 1...")
		for vec in self.STRVEC_INIT1[1:]:
			self.__loadStringVector(vec)
			self.__runCommandSync(self.ISSPCMD_SENDVEC)
		self.printDebug("Executing...")
		self.__runCommandSync(self.ISSPCMD_EXEC)
		self.printDebug("Sending vector 2...")
		for vec in self.STRVEC_INIT2:
			self.__loadStringVector(vec)
			self.__runCommandSync(self.ISSPCMD_SENDVEC)
		self.printDebug("Executing...")
		self.__runCommandSync(self.ISSPCMD_EXEC)
		self.printDebug("Sending vector 3...")
		for vec in self.STRVEC_INIT3_HIVDD:
			self.__loadStringVector(vec)
			self.__runCommandSync(self.ISSPCMD_SENDVEC)

	def __readID(self):
		"Read the silicon ID"
		for vec in self.STRVEC_IDSETUP:
			self.__loadStringVector(vec)
			self.__runCommandSync(self.ISSPCMD_SENDVEC)
		self.__runCommandSync(self.ISSPCMD_EXEC)

		low = self.__readByte(0xF8)
		high = self.__readByte(0xF9)

		return low | (high << 8)

	def __readByte(self, address):
		strVec = self.__stringVectorReplace(self.STRVEC_READBYTE, "a", address)
		self.__loadStringVector(strVec)
		self.__runCommandSync(self.ISSPCMD_SENDVEC)
		input = self.__getInputVector()
		return (input >> 2) & 0xFF

	def __loadCommand(self, command):
		self.top.cmdFPGAWrite(0x12, command & 0xFF)

	def __runCommandSync(self, command):
		self.__loadCommand(command)
		self.__busyWait()

	def __loadVectorLow(self, vecLow):
		self.top.cmdFPGAWrite(0x13, vecLow & 0xFF)

	def __loadVectorMed(self, vecMed):
		self.top.cmdFPGAWrite(0x14, vecMed & 0xFF)

	def __loadVectorHigh(self, vecHigh):
		self.top.cmdFPGAWrite(0x15, vecHigh & 0xFF)

	def __loadVector(self, vec):
		self.__loadVectorLow(vec)
		self.__loadVectorMed(vec >> 8)
		self.__loadVectorHigh(vec >> 16)

	def __loadVectorInputMaskLow(self, maskLow):
		self.top.cmdFPGAWrite(0x16, maskLow & 0xFF)

	def __loadVectorInputMaskMed(self, maskMed):
		self.top.cmdFPGAWrite(0x17, maskMed & 0xFF)

	def __loadVectorInputMaskHigh(self, maskHigh):
		self.top.cmdFPGAWrite(0x18, maskHigh & 0xFF)

	def __loadVectorInputMask(self, mask):
		self.__loadVectorInputMaskLow(mask)
		self.__loadVectorInputMaskMed(mask >> 8)
		self.__loadVectorInputMaskHigh(mask >> 16)

	def __getStatusFlags(self):
		self.top.cmdFPGAReadRaw(0x12)
		stat = self.top.cmdReadStatusReg()
		return ord(stat[0])

	def __busy(self):
		return bool(self.__getStatusFlags() & self.STAT_BUSY)

	def __busyWait(self):
#XXX		for i in range(0, 50):
		while 1:
			if not self.__busy():
				return
			time.sleep(0.01)
		self.throwError("Timeout in busywait. Chip not responding?")

	def __getInputVector(self):
		self.top.cmdFPGAReadRaw(0x13)
		self.top.cmdFPGAReadRaw(0x14)
		self.top.cmdFPGAReadRaw(0x15)
		stat = self.top.cmdReadStatusReg()
		return ord(stat[0]) | (ord(stat[1]) << 8) | (ord(stat[2]) << 16)

	def __stringVectorToBinary(self, vector):
		binary = 0
		input = 0
		assert(len(vector) == 22)
		bit = len(vector) - 1
		for b in vector:
			if b == "1":
				binary |= (1 << bit)
			if b == "H" or b == "L" or b == "Z" or b == "D":
				input |= (1 << bit)
			bit -= 1
		return (binary, input)

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

	def __loadStringVector(self, strVec):
		(vector, inputMask) = self.__stringVectorToBinary(strVec)
		self.__loadVectorInputMask(inputMask)
		self.__loadVector(vector)

RegisteredChip(
	Chip_M8C_ISSP,
	bitfile = "m8c-issp",
	description = "Cypress M8C In System Serial Programmer",
	packages = ( ("M8C ISSP header", "Special adapter"), ),
	comment = "Special adapter required",
	broken = True
)
