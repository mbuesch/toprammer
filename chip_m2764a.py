"""
#    TOP2049 Open Source programming suite
#
#    M2764A EPROM programmer
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


class M2764A(Chip):
	PROGCMD_PPULSE	= 1 # Perform a P-pulse

	STAT_BUSY	= 0x01 # Programmer is running a command

	def __init__(self):
		Chip.__init__(self, "m2764a", broken=True)

	def initializeChip(self):
		self.printDebug("Initializing chip")
		self.top.vccx.setLayoutMask(0)
		self.top.vpp.setLayoutMask(0)
		self.top.gnd.setLayoutPins( [] )
		self.top.queueCommand("\x0E\x28\x01\x00")
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(0)
		self.top.cmdSetVPPVoltage(5)

	def shutdownChip(self):
		self.printDebug("Shutdown chip")
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(5)
		self.top.vccx.setLayoutMask(0)
		self.top.vpp.setLayoutMask(0)
		self.top.gnd.setLayoutPins( [] )

	def readEEPROM(self):
		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(5)
		self.top.vccx.setLayoutPins( (38,) )
		self.top.vpp.setLayoutPins( (5, 6, 7, 9, 11) )
		self.top.gnd.setLayoutPins( (24,) )

		image = ""
		self.progressMeterInit("Reading EPROM", 0x2000)
		self.__setEG(E=1, G=1)
		for addr in range(0, 0x2000):
			self.progressMeter(addr)
			image += self.__readData(addr)
		self.__setEG(E=1, G=1)
		self.progressMeterFinish()

		return image

	def writeEEPROM(self, image):
		if len(image) != 0x2000:
			self.throwError("Invalid EPROM image size %d (expected %d)" %\
				(len(image), 0x2000))

		self.top.cmdSetVCCXVoltage(5)
		self.top.cmdSetVPPVoltage(12)
		self.top.vccx.setLayoutPins( (38,) )
		self.top.vpp.setLayoutPins( (5, 6, 7, 9, 11) )
		self.top.gnd.setLayoutPins( (24,) )

		self.progressMeterInit("Writing EPROM", 0x2000)
		self.__setEG(E=1, G=1)
		for addr in range(0, 0x2000):
			self.progressMeter(addr)
			self.__writeData(addr, ord(image[addr]))
		self.__setEG(E=1, G=1)
		self.progressMeterFinish()

	def __readData(self, addr):
		self.__loadAddr(addr)
		self.__setEG(E=0, G=0)
		self.top.cmdFPGAReadByte()
		stat = self.top.cmdReadStatusReg()
		return stat[0]

	def __writeData(self, addr, data):
		self.__setEG(E=0, G=1)
		self.__loadAddr(addr)
		self.__loadData(data)
		self.__loadPPulseLen(1)
		self.__runCommandSync(self.PROGCMD_PPULSE)
		for i in range(0, 25):
			r = ord(self.__readData(addr))
			if r == data:
				break
			self.__setEG(E=0, G=1)
			self.__runCommandSync(self.PROGCMD_PPULSE)
		else:
			self.throwError("Failed to program 0x%04X (got 0x%02X, expected 0x%02X)" %\
				(addr, r, data))
		self.__setEG(E=0, G=1)
		self.__loadPPulseLen(3 * (i + 1))
		self.__runCommandSync(self.PROGCMD_PPULSE)

	def __loadData(self, data):
		self.top.cmdFPGAWrite(0x10, data)

	def __loadCommand(self, command):
		self.top.cmdFPGAWrite(0x12, command & 0xFF)

	def __runCommandSync(self, command):
		self.__loadCommand(command)
		self.__busyWait()

	def __loadAddrLow(self, addrLow):
		self.top.cmdFPGAWrite(0x13, addrLow & 0xFF)

	def __loadAddrHigh(self, addrHigh):
		self.top.cmdFPGAWrite(0x14, addrHigh & 0xFF)

	def __loadAddr(self, addr):
		self.__loadAddrLow(addr)
		self.__loadAddrHigh(addr >> 8)

	def __loadPPulseLen(self, msec):
		self.top.cmdFPGAWrite(0x15, msec)

	def __setEG(self, E, G):
		data = 0
		if E:
			data |= 1
		if G:
			data |= 2
		self.top.cmdFPGAWrite(0x16, data)

	def __getStatusFlags(self):
		self.top.cmdFPGAReadRaw(0x12)
		stat = self.top.cmdReadStatusReg()
		return ord(stat[0])

	def __busy(self):
		return bool(self.__getStatusFlags() & self.STAT_BUSY)

	def __busyWait(self):
		for i in range(0, 100):
			if not self.__busy():
				return
			self.top.delay(0.01)
		self.throwError("Timeout in busywait.")

supportedChips.append(M2764A())
