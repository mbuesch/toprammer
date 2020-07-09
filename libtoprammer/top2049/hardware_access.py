"""
#    TOP2049 Open Source programming suite
#
#    TOP2049 Lowlevel hardware access
#
#    Copyright (c) 2012 Michael Buesch <m@bues.ch>
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

from libtoprammer.util import *
from libtoprammer.hardware_access_usb import *


class HardwareAccess(HardwareAccessUSB):
	"TOP2049 hardware access"

	ADDR_OK_BIT	= 4

	def __init__(self, foundUSBDev,
		     noQueue=False, doRawDump=False):
		HardwareAccessUSB.__init__(self,
			usbdev = foundUSBDev.usbdev,
			maxPacketBytes = 64,
			noQueue = noQueue,
			doRawDump = doRawDump)

	def getOscillatorHz(self):
		"Get the 'OSC' frequency."
		return 24000000

	def getBufferRegSize(self):
		"Get the buffer register size, in bytes."
		return 64

	def readBufferReg(self, nrBytes):
		"Reads and returns the buffer register from hardware."
		self.queueCommand(int2byte(0x07))
		return self.receive(self.getBufferRegSize())[:nrBytes]

	def hardwareInit(self):
		"Initialize the hardware."
		self.queueCommand(b"\x0D")
		if self.readBufferReg(4) != b"\x69\x0C\x02\x00":
			print("Init: Unexpected status (a)")

		self.setVPPVoltage(0)
		self.setVPPVoltage(0)
		self.queueCommand(b"\x0E\x20\x00\x00")
		self.delay(0.01)
		self.setVCCVoltage(0)

		self.loadGNDLayout(0)
		self.loadVPPLayout(0)
		self.loadVCCLayout(0)

		self.queueCommand(b"\x0E\x20\x00\x00")
		self.delay(0.01)
		self.queueCommand(b"\x0E\x25\x00\x00")
		if self.readBufferReg(4) != b"\x6C\x68\x00\x00":
			print("Init: Unexpected status (b)")
		self.enableZifPullups(False)
		self.flushCommands()

	def readVersionString(self):
		"Returns the device ID and versioning string."
		self.queueCommand(b"\x0E\x11\x00\x00")
		data = self.readBufferReg(16)
		return data.decode("ASCII", "ignore").strip()

	def getFPGAType(self):
		"Get the FPGA architecture."
		return "xc2s15"

	def getFPGAMaxConfigChunkSize(self):
		"Maximum config chunk size."
		return 60

	def FPGAInitiateConfig(self):
		"Initiate a configuration sequence on the FPGA."
		self.queueCommand(b"\x0E\x21\x00\x00")
		stat = byte2int(self.readBufferReg(1))
		expected = 0x01
		if stat != expected:
			raise TOPException("bit-upload: Failed to initiate " +\
				"config sequence (got 0x%02X, expected 0x%02X)" %\
				(stat, expected))

	def FPGAUploadConfig(self, offset, data):
		"Upload configuration data into the FPGA."
		assert(len(data) <= self.getFPGAMaxConfigChunkSize())
		cmd = b"\x0E\x22\x00\x00" + data
		cmd += b"\x00" * (64 - len(cmd)) # padding
		self.queueCommand(cmd)

	def makeFPGAAddr(self, address):
		# Set the "address OK" bit
		return address | (1 << self.ADDR_OK_BIT)

	def FPGARead(self, address):
		"Do an FPGA read at 'address'. Data is put into buffer reg."
		address = self.makeFPGAAddr(address)
		if address == self.makeFPGAAddr(0): # Fast tracked
			self.queueCommand(int2byte(0x01))
			return
		self.queueCommand(int2byte(0x0B) + int2byte(address))

	def FPGAWrite(self, address, byte):
		"Write 'byte' to FPGA at 'address'."
		address = self.makeFPGAAddr(address)
		if address == self.makeFPGAAddr(0): # Fast tracked
			self.queueCommand(int2byte(0x10) + int2byte(byte))
			return
		self.queueCommand(int2byte(0x0A) + int2byte(address) +\
				  int2byte(byte))

	def loadGNDLayout(self, layout):
		"Load the GND configuration into the H/L shiftregisters."
		cmd = int2byte(0x0E) + int2byte(0x16) +\
		      int2byte(layout) + int2byte(0)
		self.queueCommand(cmd)
		self.delay(0.01)
		self.flushCommands(0.15)

	def setVPPVoltage(self, voltage):
		"Set the VPP voltage. voltage is a floating point voltage number."
		centivolt = int(voltage * 10)
		cmd = int2byte(0x0E) + int2byte(0x12) +\
		      int2byte(centivolt) + int2byte(0)
		self.queueCommand(cmd)
		self.delay(0.01)

	def loadVPPLayout(self, layout):
		"Load the VPP configuration into the shift registers."
		cmd = int2byte(0x0E) + int2byte(0x14) +\
		      int2byte(layout) + int2byte(0)
		self.queueCommand(cmd)
		self.delay(0.01)
		self.flushCommands(0.15)

	def setVCCVoltage(self, voltage):
		"Set the VCC voltage."
		centivolt = int(voltage * 10)
		cmd = int2byte(0x0E) + int2byte(0x13) +\
		      int2byte(centivolt) + int2byte(0)
		self.queueCommand(cmd)
		self.delay(0.01)

	def loadVCCLayout(self, layout):
		"Load the VCC configuration into the shift registers."
		cmd = int2byte(0x0E) + int2byte(0x15) +\
		      int2byte(layout) + int2byte(0)
		self.queueCommand(cmd)
		self.delay(0.01)
		self.flushCommands(0.15)

	def enableZifPullups(self, enable):
		"Enable the ZIF socket signal pullups."
		param = 1 if enable else 0
		cmd = int2byte(0x0E) + int2byte(0x28) +\
		      int2byte(param) + int2byte(0)
		self.queueCommand(cmd)

	def __delay_4usec(self):
		self.queueCommand(int2byte(0x00))

	def __delay_10msec(self):
		self.queueCommand(int2byte(0x1B))

	def delay(self, seconds):
		"Perform an on-device or host delay."
		if seconds >= 0.5:
			# Perform long delays on the host
			self.flushCommands(seconds)
			return
		if seconds > 0.000255:
			# Need to round up to ten milliseconds
			millisecs = int(math.ceil(seconds * 1000))
			millisecs = roundup(millisecs, 10)
			for i in range(0, millisecs // 10):
				self.__delay_10msec()
		else:
			# Round up to 4 usec boundary
			microsecs = int(math.ceil(seconds * 1000000))
			microsecs = roundup(microsecs, 4)
			for i in range(0, microsecs // 4):
				self.__delay_4usec()
