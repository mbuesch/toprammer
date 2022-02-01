"""
#    TOP Open Source programming suite
#
#    TOP853 Lowlevel hardware access
#
#    Copyright (c) 2022 Michael Buesch <m@bues.ch>
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
	"TOP853 hardware access"

	def __init__(self, foundUSBDev, noQueue=False, doRawDump=False):
		HardwareAccessUSB.__init__(self,
			usbdev = foundUSBDev.usbdev,
			maxPacketBytes = 64,
			noQueue = noQueue,
			doRawDump = doRawDump)

	def getOscillatorHz(self):
		"Get the 'OSC' frequency."
		return 8000000

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
		if self.readBufferReg(3) != b"\x69\x0C\x02":
			print("Init: Unexpected status (a)")

		self.runCommandSync(b"\x0E\x2C\x01\x00")
		for i in range(0x18):
			self.queueCommand(b"\x3E" + int2byte(i))
		if self.readBufferReg(4) != b"\x24\x37\x55\x04":
			print("Init: Unexpected status (b)")

		self.setVPPVoltage(0)

		for i in range(0x18):
			self.queueCommand(b"\x3E" + int2byte(i))
		if self.readBufferReg(4) != b"\x24\x37\x55\x04":
			print("Init: Unexpected status (c)")

		self.setVPPVoltage(12)

		self.runCommandSync(b"\x0E\x20\x00\x00")
		self.__delay_10msec(sync=True)

		self.runCommandSync(b"\x0E\x13\x00\x00")
		self.__delay_10msec(sync=True)

		self.runCommandSync(b"\x0A\x1D\x86")
		self.flushCommands()

		self.loadGNDLayout(0)
		self.loadVPPLayout(0)
		self.loadVCCLayout(0)

		for i in range(0x18):
			self.queueCommand(b"\x3E" + int2byte(i))
		if self.readBufferReg(4) != b"\x24\x37\x55\x04":
			print("Init: Unexpected status (c)")

		self.setVPPVoltage(12)

		self.runCommandSync(b"\x0E\x20\x00\x00")
		self.__delay_10msec(sync=True)

		for _ in range(2):
			self.queueCommand(b"\x57\x00\x50")
			if self.readBufferReg(4) != b"\xB0\x37\x55\x04":
				print("Init: Unexpected status (d)")

		for i in range(0x18):
			self.queueCommand(b"\x3E" + int2byte(i))
		if self.readBufferReg(4) != b"\x24\x37\x55\x04":
			print("Init: Unexpected status (c)")

		for i in range(0x20, 0x24):
			self.runCommandSync(b"\x57\x00" + int2byte(i))
		if self.readBufferReg(4) != b"\x80\xBE\x90\x00":
			print("Init: Unexpected status (e)")

		for i in range(0x40, 0x60):
			self.runCommandSync(b"\x57\x00" + int2byte(i))
		if self.readBufferReg(32) != b"\x54\x15\x62\x9E\x6E\xCB\xED\x5D\x15\x32\x70\x81\x05\xF9\x4F\x2E\xB0\x3C\x7E\x7B\x02\x40\x0B\x48\x28\x78\x63\x1D\x0C\x39\x3B\x79":
			print("Init: Unexpected status (f)")

		self.queueCommand(b"\x4F\x02\x00\x00")
		if self.readBufferReg(32) != b"\x48\xFF\x6F\x06\x49\x65\x52\x57\x52\x15\x20\x87\x05\xF9\x4F\x2E\xB0\x3C\x7E\x7B\x02\x40\x0B\x48\x28\x78\x63\x1D\x0C\x39\x3B\x79":
			print("Init: Unexpected status (g)")

		self.runCommandSync(b"\x0E\x10\x00\x00")
		self.runCommandSync(b"\x0E\x2D\x01\x00" + b"\x00\x00" + (b"\x33" * 57))
		self.runCommandSync(b"\x0E\x2D\x02\x00" + (b"\x33" * 56))
		self.runCommandSync(b"\x0E\x2D\x03\x00" + b"\x28" + (b"\x33" * 31) + b"\x00\x00\x00\x00")

		self.loadGNDLayout(20)

		for i in range(0x18):
			self.queueCommand(b"\x3E" + int2byte(i))
		if self.readBufferReg(4) != b"\x24\x37\x55\x04":
			print("Init: Unexpected status (h)")

		self.setVPPVoltage(12)

#		import libtoprammer.top853.sniffer as sniffer
#		sniffer.sniffVPP(self)
		#TODO
		self.flushCommands()
		assert 0#XXX

	def readVersionString(self):
		"Returns the device ID and versioning string."
		self.queueCommand(b"\x0E\x11\x00\x00")
		data = self.readBufferReg(32)
		return data.decode("ASCII", "ignore").replace("\x00", "").strip()

	def getFPGAType(self):
		"Get the FPGA architecture."
		return None # The hardware doesn't have an FPGA.

	def getFPGAMaxConfigChunkSize(self):
		raise NotImplementedError

	def FPGAInitiateConfig(self):
		raise NotImplementedError

	def FPGAUploadConfig(self, offset, data):
		raise NotImplementedError

	def makeFPGAAddr(self, address):
		raise NotImplementedError

	def FPGARead(self, address):
		raise NotImplementedError

	def FPGAWrite(self, address, byte):
		raise NotImplementedError

	def loadGNDLayout(self, layout):
		"Load the GND configuration into the shift registers."
		cmd = int2byte(0x0E) + int2byte(0x16) +\
		      int2byte(layout) + int2byte(0)
		self.queueCommand(cmd)
		self.delay(0.01)
		self.flushCommands(0.15)

	def setVPPVoltage(self, voltage):
		"Set the VPP voltage. voltage is a floating point voltage number."
		for centivolt in (0, int(voltage * 10)):
			cmd = int2byte(0x0E) + int2byte(0x0F) +\
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
		"Set the VCC voltage. This is a no-op. The programmer can only do 5V."
		assert voltage == 0 or voltage == 5
		self.flushCommands()

	def loadVCCLayout(self, layout):
		"Load the VCC configuration into the shift registers."
		cmd = int2byte(0x0E) + int2byte(0x15) +\
		      int2byte(layout) + int2byte(0)
		self.queueCommand(cmd)
		self.delay(0.01)
		self.flushCommands(0.15)

	def enableZifPullups(self, enable):
		#TODO
		"Enable the ZIF socket signal pullups."
		param = 1 if enable else 0
		cmd = int2byte(0x0E) + int2byte(0x28) +\
		      int2byte(param) + int2byte(0)
		self.queueCommand(cmd)

	def __delay_4usec(self):
		#TODO
		self.queueCommand(int2byte(0x00))

	def __delay_10msec(self, sync=False):
		#TODO
		if sync:
			self.runCommandSync(int2byte(0x1B))
		else:
			self.queueCommand(int2byte(0x1B))

	def delay(self, seconds):
		"Perform an on-device or host delay."
		if seconds >= 0.5:
			# Perform long delays on the host
			self.flushCommands(seconds)
		elif seconds > 0.000255:
			# Need to round up to ten milliseconds
			millisecs = int(math.ceil(seconds * 1e3))
			millisecs = roundup(millisecs, 10)
			for _ in range(millisecs // 10):
				self.__delay_10msec()
		else:
			# Round up to 4 usec boundary
			microsecs = int(math.ceil(seconds * 1e6))
			microsecs = roundup(microsecs, 4)
			for _ in range(microsecs // 4):
				self.__delay_4usec()
