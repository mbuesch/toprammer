"""
#    TOP2049 Open Source programming suite
#
#    Copyright (c) 2009-2011 Michael Buesch <mb@bu3sch.de>
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

VERSION_MAJOR	= 0
VERSION_MINOR	= 8
VERSION = "%d.%d" % (VERSION_MAJOR, VERSION_MINOR)

from bitfile import *
from util import *

import sys
import time
import re
try:
	import usb
except (ImportError), e:
	print "Python USB support module not found. Please install python-usb."
	sys.exit(1)

from top_xxxx import *
from chip_xxxx import *
from user_interface import *


class TOP:
	# Supported programmer types
	TYPE_TOP2049		= "TOP2049"

	def __init__(self, busDev=None, verbose=0,
		     forceLevel=0, noqueue=False, usebroken=False,
		     forceBitfileUpload=False,
		     userInterface=ConsoleUserInterface()):
		"""busDev is a tuple (BUSID, DEVID) or None."""

		self.verbose = verbose
		self.forceLevel = forceLevel
		self.forceBitfileUpload = forceBitfileUpload
		self.noqueue = noqueue
		self.usebroken = usebroken
		self.userInterface = userInterface

		self.chip = None
		self.commandQueue = []

		# Find the device
		for bus in usb.busses():
			if busDev and bus.dirname != "%03d" % busDev[0]:
				continue
			for dev in bus.devices:
				if busDev and dev.filename != "%03d" % busDev[1]:
					continue
				if self.__isTOP(dev):
					break
				if busDev:
					raise TOPException(
						"Device %03d.%03d is not a TOP device" %\
						(busDev[0], busDev[1]))
			else:
				continue
			break
		else:
			raise TOPException("TOP programmer device not found!")
		self.usbbus = bus
		self.usbdev = dev
		self.usbh = None

		if self.noqueue:
			self.printWarning("WARNING: Command queuing disabled. " +\
				"Hardware access will be _really_ slow.")

		self.initializeProgrammer()

	def initializeChip(self, chipID):
		"Initialize the programmer for a chip"
		# If a chip is initialized, shut it down first.
		if self.chip:
			self.shutdownChip()
		# Find the implementation of the chip.
		(descriptor, self.chip) = ChipDescription.findOne(self.topType, chipID, self.usebroken)
		self.chip.setTOP(self)
		# Find the bitfile for the chip.
		bitfile = bitfileFind(descriptor.bitfile)
		if not bitfile:
			self.chip = None
			raise TOPException("Did not find BIT-file for chip implementation %s" % chipID)
		# Open and parse the bitfile.
		self.bitfile = Bitfile()
		self.bitfile.parseFile(bitfile)
		# Initialize the hardware.
		self.__bitfileUpload(descriptor.runtimeID)

	def shutdownChip(self):
		if self.chip:
			self.chip.shutdownChip()
			self.flushCommands()
			self.chip = None

	def resetChip(self):
		if self.chip:
			self.chip.shutdownChip()
			self.flushCommands()

	def getChip(self):
		"Get the chip. May return None"
		return self.chip

	def checkChip(self):
		if not self.chip:
			raise TOPException("Target chip not selected")

	def getForceLevel(self):
		return self.forceLevel

	def progressMeterInit(self, meterId, message, nrSteps):
		if self.verbose >= 1:
			self.userInterface.progressMeterInit(meterId, message, nrSteps)

	def progressMeterFinish(self, meterId):
		if self.verbose >= 1:
			self.userInterface.progressMeterFinish(meterId)

	def progressMeter(self, meterId, step):
		if self.verbose >= 1:
			self.userInterface.progressMeter(meterId, step)

	def printWarning(self, message):
		if self.verbose >= 0:
			self.flushCommands()
			self.userInterface.warningMessage(message)

	def printInfo(self, message):
		if self.verbose >= 1:
			self.flushCommands()
			self.userInterface.infoMessage(message)

	def printDebug(self, message):
		if self.verbose >= 2:
			self.flushCommands()
			self.userInterface.debugMessage(message)

	@staticmethod
	def __isTOP(usbdev):
		"Returns true, if the USB device is a supported TOP programmer device."
		ids = (
			(0x2471, 0x0853),	# TOP2049
		)
		return (usbdev.idVendor, usbdev.idProduct) in ids

	def __initializeUSB(self):
		# Set up the USB interface
		self.__shutdownUSB()
		try:
			self.usbh = self.usbdev.open()
			config = self.usbdev.configurations[0]
			interface = config.interfaces[0][0]

			# Find the endpoints
			self.bulkOut = None
			self.bulkIn = None
			for ep in interface.endpoints:
				if not self.bulkIn and \
				   ep.type == usb.ENDPOINT_TYPE_BULK and \
				   (ep.address & (usb.ENDPOINT_IN | usb.ENDPOINT_OUT)) == usb.ENDPOINT_IN:
					self.bulkIn = ep
				if not self.bulkOut and \
				   ep.type == usb.ENDPOINT_TYPE_BULK and \
				   (ep.address & (usb.ENDPOINT_IN | usb.ENDPOINT_OUT)) == usb.ENDPOINT_OUT:
					self.bulkOut = ep
			if not self.bulkIn or not self.bulkOut:
				raise TOPException("Did not find all USB EPs")

			self.usbh.setConfiguration(config)
			self.usbh.claimInterface(interface)
			self.usbh.setAltInterface(interface)
			self.usbh.clearHalt(self.bulkOut.address)
			self.usbh.clearHalt(self.bulkIn.address)
		except (usb.USBError), e:
			self.usbh = None
			raise TOPException("USB error: " + str(e))

	def __shutdownUSB(self):
		try:
			if self.usbh:
				self.usbh.releaseInterface()
				self.usbh = None
		except (usb.USBError), e:
			raise TOPException("USB error: " + str(e))

	def initializeProgrammer(self):
		"Initialize the hardware"

		self.__initializeUSB()

		versionRegex = (
			(r"top2049\s+ver\s*(\d+\.\d+)", self.TYPE_TOP2049),
		)

		versionString = self.cmdRequestVersion()
		for (regex, topType) in versionRegex:
			m = re.match(regex, versionString, re.IGNORECASE)
			if m:
				self.topType = topType
				self.topVersion = m.group(1)
				break
		else:
			raise TOPException("Connected TOP programmer '" + versionString +\
				"' is not supported by Toprammer, yet")
		self.printInfo("Initializing the " + self.topType + " version " + self.topVersion)

		# Initialize the programmer specific layouts
		if self.topType == self.TYPE_TOP2049:
			self.vccx = top2049.vccx_layouts.VCCXLayout(self)
			self.vpp = top2049.vpp_layouts.VPPLayout(self)
			self.gnd = top2049.gnd_layouts.GNDLayout(self)
		else:
			assert(0)

		self.queueCommand("\x0D")
		stat = self.cmdReadBufferReg32()
		if stat != 0x00020C69:
			self.printWarning("Init: Unexpected status (a): 0x%08X" % stat)

		self.cmdSetVPPVoltage(0)
		self.cmdSetVPPVoltage(0)
		self.queueCommand("\x0E\x20\x00\x00")
		self.cmdDelay(0.01)
		self.cmdSetVCCXVoltage(0)

		self.cmdLoadGNDLayout(0)
		self.cmdLoadVPPLayout(0)
		self.cmdLoadVCCXLayout(0)

		self.queueCommand("\x0E\x20\x00\x00")
		self.cmdDelay(0.01)
		self.queueCommand("\x0E\x25\x00\x00")
		stat = self.cmdReadBufferReg32()
		if stat != 0x0000686C:
			self.printWarning("Init: Unexpected status (b): 0x%08X" % stat)
		self.cmdEnableZifPullups(False)
		self.flushCommands()

	def shutdownProgrammer(self):
		self.__shutdownUSB()
		self.topType = None
		self.topVersion = None

	def getProgrammerType(self):
		return self.topType

	def getProgrammerVersion(self):
		return self.topVersion

	def __readBitfileID(self):
		self.cmdFPGARead(0xFD)
		self.cmdFPGARead(0xFE)
		self.cmdFPGARead(0xFF)
		data = self.cmdReadBufferReg(3)
		gotID = ord(data[0]) | (ord(data[1]) << 8)
		if gotID == 0xFEFD or gotID == 0xFFFF:
			gotID = 0
		gotRev = ord(data[2])
		if gotRev == 0xFF:
			gotRev = 0
		return (gotID, gotRev)

	def __bitfileUpload(self, requiredRuntimeID):
		(requiredID, requiredRevision) = requiredRuntimeID
		if requiredID and requiredRevision and not self.forceBitfileUpload:
			# Check if the bitfile is already uploaded.
			(gotID, gotRev) = self.__readBitfileID()
			if gotID == requiredID and gotRev == requiredRevision:
				self.printDebug("Bitfile %s ID 0x%04X Rev 0x%02X is already uploaded." %\
						(self.bitfile.getFilename(), gotID, gotRev))
				return
			self.printDebug("Current runtime ID 0x%04X Rev 0x%02X. Uploading new bitfile..." %\
					(gotID, gotRev))

		self.printDebug("Uploading bitfile %s..." % self.bitfile.getFilename())

		self.cmdFPGAInitiateConfig()
		stat = self.cmdReadBufferReg8()
		expected = 0x01
		if stat != expected:
			raise TOPException("bit-upload: Failed to initiate " +\
				"config sequence (got 0x%02X, expected 0x%02X)" %\
				(stat, expected))

		data = self.bitfile.getPayload()
		for i in range(0, len(data), 60):
			self.cmdFPGAUploadConfig(data[i : i + 60])
		self.flushCommands()

		if requiredID and requiredRevision:
			# Check the uploaded ID
			(gotID, gotRev) = self.__readBitfileID()
			if gotID != requiredID or gotRev != requiredRevision:
				raise TOPException("bit-upload: The bitfile upload succeed, "
					"but the read ID or revision is invalid. "
					"(Got 0x%04X/0x%02X, but expected 0x%04X/0x%02X)" %\
					(gotID, gotRev, requiredID, requiredRevision))

	def readSignature(self):
		"""Reads the chip signature and returns it."""
		self.printDebug("Reading signature from chip...")
		self.checkChip()
		sig = self.chip.readSignature()
		self.flushCommands()
		self.printDebug("Done reading %d bytes." % len(sig))
		return sig

	def eraseChip(self):
		"""Erase the chip."""
		self.printDebug("Erasing chip...")
		self.checkChip()
		self.chip.erase()
		self.flushCommands()

	def testChip(self):
		"""Run a unit-test on the chip."""
		self.printDebug("Running chip unit-test...")
		self.checkChip()
		self.chip.test()
		self.flushCommands()
		self.printInfo("Chip unit-test terminated successfully.")

	def readProgmem(self):
		"""Reads the program memory image and returns it."""
		self.printDebug("Reading program memory from chip...")
		self.checkChip()
		image = self.chip.readProgmem()
		self.flushCommands()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeProgmem(self, image):
		"""Writes a program memory image to the chip."""
		self.printDebug("Writing %d bytes of program memory to chip..." % len(image))
		self.checkChip()
		self.chip.writeProgmem(image)
		self.flushCommands()
		self.printDebug("Done writing image.")

	def readEEPROM(self):
		"""Reads the EEPROM image and returns it."""
		self.printDebug("Reading EEPROM from chip...")
		self.checkChip()
		image = self.chip.readEEPROM()
		self.flushCommands()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeEEPROM(self, image):
		"""Writes an EEPROM image to the chip."""
		self.printDebug("Writing %d bytes of EEPROM to chip..." % len(image))
		self.checkChip()
		self.chip.writeEEPROM(image)
		self.flushCommands()
		self.printDebug("Done writing image.")

	def readFuse(self):
		"""Reads the fuses image and returns it."""
		self.printDebug("Reading fuses from chip...")
		self.checkChip()
		image = self.chip.readFuse()
		self.flushCommands()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeFuse(self, image):
		"""Writes a fuses image to the chip."""
		self.printDebug("Writing %d bytes of fuses to chip..." % len(image))
		self.checkChip()
		self.chip.writeFuse(image)
		self.flushCommands()
		self.printDebug("Done writing image.")

	def readLockbits(self):
		"""Reads the Lock bits image and returns it."""
		self.printDebug("Reading lock-bits from chip...")
		self.checkChip()
		image = self.chip.readLockbits()
		self.flushCommands()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeLockbits(self, image):
		"""Writes a Lock bits image to the chip."""
		self.printDebug("Writing %d bytes of lock-bits to chip..." % len(image))
		self.checkChip()
		self.chip.writeLockbits(image)
		self.flushCommands()
		self.printDebug("Done writing image.")

	def readRAM(self):
		"""Reads the RAM and returns it."""
		self.printDebug("Reading RAM from chip...")
		self.checkChip()
		image = self.chip.readRAM()
		self.flushCommands()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeRAM(self, image):
		"""Writes the RAM image to the chip."""
		self.printDebug("Writing %d bytes of RAM to the chip..." % len(image))
		self.checkChip()
		self.chip.writeRAM(image)
		self.flushCommands()
		self.printDebug("Done writing the image.")

	def __cmdDelay_4usec(self):
		self.queueCommand(chr(0x00))

	def __cmdDelay_10msec(self):
		self.queueCommand(chr(0x1B))

	def cmdDelay(self, seconds):
		"""Send a delay request to the device. Note that this causes the
		programmer to execute the delay. For a host-delay, use hostDelay()"""
		assert(seconds < 0.5)
		if seconds > 0.000255:
			# Need to round up to ten milliseconds
			millisecs = int(math.ceil(seconds * 1000))
			millisecs = roundup(millisecs, 10)
			for i in range(0, millisecs // 10):
				self.__cmdDelay_10msec()
		else:
			# Round up to 4 usec boundary
			microsecs = int(math.ceil(seconds * 1000000))
			microsecs = roundup(microsecs, 4)
			for i in range(0, microsecs // 4):
				self.__cmdDelay_4usec()

	def hostDelay(self, seconds):
		"""Flush all commands and delay the host computer for 'seconds'"""
		self.flushCommands()
		time.sleep(seconds)

	def getOscillatorHz(self):
		"""Returns the FPGA oscillator frequency, in Hz.
		The oscillator is connected to the FPGA clk pin."""
		return 24000000

	def getBufferRegSize(self):
		"""Returns the size (in bytes) of the buffer register."""
		return 64

	def cmdReadBufferReg(self, nrBytes=-1):
		"""Read the buffer register. Returns nrBytes (default all bytes)."""
		regSize = self.getBufferRegSize()
		if nrBytes < 0:
			nrBytes = regSize
		assert(nrBytes <= regSize)
		if not nrBytes:
			return ""
		self.queueCommand(chr(0x07))
		return self.receive(regSize)[0:nrBytes]

	def cmdReadBufferReg8(self):
		"""Read a 8bit value from the buffer register."""
		stat = self.cmdReadBufferReg(1)
		stat = ord(stat[0])
		return stat

	def cmdReadBufferReg16(self):
		"""Read a 16bit value from the buffer register."""
		stat = self.cmdReadBufferReg(2)
		stat = ord(stat[0]) | (ord(stat[1]) << 8)
		return stat

	def cmdReadBufferReg24(self):
		"""Read a 24bit value from the buffer register."""
		stat = self.cmdReadBufferReg(3)
		stat = ord(stat[0]) | (ord(stat[1]) << 8) | (ord(stat[2]) << 16)
		return stat

	def cmdReadBufferReg32(self):
		"""Read a 32bit value from the buffer register."""
		stat = self.cmdReadBufferReg(4)
		stat = ord(stat[0]) | (ord(stat[1]) << 8) | \
		       (ord(stat[2]) << 16) | (ord(stat[3]) << 24)
		return stat

	def cmdReadBufferReg48(self):
		"""Read a 48bit value from the buffer register."""
		stat = self.cmdReadBufferReg(6)
		stat = ord(stat[0]) | (ord(stat[1]) << 8) | \
		       (ord(stat[2]) << 16) | (ord(stat[3]) << 24) | \
		       (ord(stat[4]) << 32) | (ord(stat[5]) << 40)
		return stat

	def cmdRequestVersion(self):
		"""Returns the device ID and versioning string."""
		self.queueCommand("\x0E\x11\x00\x00")
		data = self.cmdReadBufferReg(16)
		return data.strip()

	def cmdFPGAInitiateConfig(self):
		"""Initiate a configuration sequence on the FPGA."""
		self.queueCommand("\x0E\x21\x00\x00")

	def cmdFPGAUploadConfig(self, data):
		"""Upload configuration data into the FPGA."""
		assert(len(data) <= 60)
		cmd = "\x0E\x22\x00\x00" + data
		cmd += "\x00" * (64 - len(cmd)) # padding
		self.queueCommand(cmd)

	def cmdFPGARead(self, address):
		"""Read a byte from the FPGA at address into the buffer register."""
		if address == 0x10: # Fast tracked
			self.queueCommand(chr(0x01))
			return
		self.queueCommand(chr(0x0B) + chr(address))

	def cmdFPGAWrite(self, address, byte):
		"""Write a byte to an FPGA address."""
		if address == 0x10: # Fast tracked
			self.queueCommand(chr(0x10) + chr(byte))
			return
		self.queueCommand(chr(0x0A) + chr(address) + chr(byte))

	def cmdLoadGNDLayout(self, layout):
		"""Load the GND configuration into the H/L shiftregisters."""
		cmd = chr(0x0E) + chr(0x16) + chr(layout) + chr(0)
		self.queueCommand(cmd)
		self.cmdDelay(0.01)
		self.hostDelay(0.15)

	def cmdSetVPPVoltage(self, voltage):
		"""Set the VPP voltage. voltage is a floating point voltage number."""
		centivolt = int(voltage * 10)
		cmd = chr(0x0E) + chr(0x12) + chr(centivolt) + chr(0)
		self.queueCommand(cmd)
		self.cmdDelay(0.01)

	def cmdLoadVPPLayout(self, layout):
		"""Load the VPP configuration into the shift registers."""
		cmd = chr(0x0E) + chr(0x14) + chr(layout) + chr(0)
		self.queueCommand(cmd)
		self.cmdDelay(0.01)
		self.hostDelay(0.15)

	def cmdSetVCCXVoltage(self, voltage):
		"""Set the VCCX voltage. voltage is a floating point voltage number."""
		centivolt = int(voltage * 10)
		cmd = chr(0x0E) + chr(0x13) + chr(centivolt) + chr(0)
		self.queueCommand(cmd)
		self.cmdDelay(0.01)

	def cmdLoadVCCXLayout(self, layout):
		"""Load the VCCX configuration into the shift registers."""
		cmd = chr(0x0E) + chr(0x15) + chr(layout) + chr(0)
		self.queueCommand(cmd)
		self.cmdDelay(0.01)
		self.hostDelay(0.15)

	def cmdEnableZifPullups(self, enable):
		"""Enable the ZIF socket signal pullups."""
		param = 0
		if enable:
			param = 1
		cmd = chr(0x0E) + chr(0x28) + chr(param) + chr(0)
		self.queueCommand(cmd)

	def __doSend(self, command):
		try:
			assert(len(command) <= 64)
			if self.verbose >= 3:
				print "Sending command:"
				dumpMem(command)
			ep = self.bulkOut.address
			self.usbh.bulkWrite(ep, command)
		except (usb.USBError), e:
			raise TOPException("USB bulk write error: " + str(e))

	def queueCommand(self, command):
		"""Queue a raw command for transmission."""
		assert(len(command) <= 64)
		if self.noqueue:
			self.__doSend(command)
		else:
			self.commandQueue.append(command)

	def runCommandSync(self, command):
		"""Run a command synchronously.
		Warning: This is slow. Don't use it unless there's a very good reason."""
		self.flushCommands()
		self.queueCommand(command)
		self.flushCommands()

	def receive(self, size):
		"""Receive 'size' bytes on the bulk-in ep."""
		# If there are blocked commands in the queue, send them now.
		self.flushCommands()
		try:
			ep = self.bulkIn.address
			data = "".join(map(lambda b: chr(b),
					   self.usbh.bulkRead(ep, size)))
			if len(data) != size:
				raise TOPException("USB bulk read error: Could not read the " +\
					"requested number of bytes (req %d, got %d)" % (size, len(data)))
			if self.verbose >= 3:
				print "Received data:"
				dumpMem(data)
		except (usb.USBError), e:
			raise TOPException("USB bulk read error: " + str(e))
		return data

	def flushCommands(self):
		"""Flush the command queue."""
		command = ""
		for oneCommand in self.commandQueue:
			assert(len(oneCommand) <= 64)
			if len(command) + len(oneCommand) > 64:
				self.__doSend(command)
				command = ""
			command += oneCommand
		if command:
			self.__doSend(command)
		self.commandQueue = []
