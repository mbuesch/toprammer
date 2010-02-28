"""
#    TOP2049 Open Source programming suite
#
#    Copyright (c) 2009-2010 Michael Buesch <mb@bu3sch.de>
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
VERSION_MINOR	= 3
VERSION = "%d.%d" % (VERSION_MAJOR, VERSION_MINOR)

from bitfile import *
from util import *

import sys
import time
try:
	import usb
except (ImportError), e:
	print "Python USB support module not found. Please install python-usb."
	sys.exit(1)

from top_xxxx import *

# Import the supported chip modules
from chip_atmega32dip40 import *
from chip_atmega8dip28 import *
from chip_atmega88dip28 import *
from chip_attiny26dip20 import *
from chip_m2764a import *
from chip_m8cissp import *
from chip_unitest import *


class TOP:
	def __init__(self, bitfileName, busDev=None, verbose=0,
		     forceLevel=0, noqueue=False, usebroken=False):
		"""bitfileName is the path to the .bit file.
		   busDev is a tuple (BUSID, DEVID) or None."""

		self.verbose = verbose
		self.forceLevel = forceLevel
		self.noqueue = noqueue
		self.usebroken = usebroken

		self.commandQueue = []

		self.bitfile = Bitfile()
		self.bitfile.parseFile(bitfileName)

		# Find a chip handler for the given bitfile.
		chipID = self.bitfile.getSrcFile().lower()
		if chipID.endswith(".ncd"):
			chipID = chipID[0:-4]
		self.chip = chipFind(chipID)
		if self.chip and self.chip.isBroken() and not usebroken:
			self.chip = None
		if not self.chip:
			raise TOPException("Did not find an implementation for the chip %s" % chipID)
		self.chip.setTOP(self)

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
		self.bulkOut = None
		self.bulkIn = None

		# Set up the USB interface
		try:
			self.usbh = self.usbdev.open()
			config = self.usbdev.configurations[0]
			interface = config.interfaces[0][0]

			# Find the endpoints
			for ep in interface.endpoints:
				if not self.bulkIn and \
				   ep.type == usb.ENDPOINT_TYPE_BULK and \
				   (ep.address & usb.ENDPOINT_IN) != 0:
					self.bulkIn = ep
				if not self.bulkOut and \
				   ep.type == usb.ENDPOINT_TYPE_BULK and \
				   (ep.address & usb.ENDPOINT_IN) == 0:
					self.bulkOut = ep
			if not self.bulkIn or not self.bulkOut:
				raise TOPException("Did not find all USB EPs")

			self.usbh.setConfiguration(config)
			self.usbh.claimInterface(interface)
			self.usbh.setAltInterface(interface)
			self.usbh.clearHalt(self.bulkOut.address)
			self.usbh.clearHalt(self.bulkIn.address)
		except (usb.USBError), e:
			raise TOPException("USB error: " + str(e))

		if self.noqueue:
			self.printWarning("WARNING: Command queuing disabled. " +\
				"Hardware access will be _really_ slow.")

		# For now we assume a TOP2049
		self.vccx = top2049.vccx_layouts.VCCXLayout(self)
		self.vpp = top2049.vpp_layouts.VPPLayout(self)
		self.gnd = top2049.gnd_layouts.GNDLayout(self)

		self.__initializeHardware()

	def shutdown(self):
		self.chip.shutdownChip()
		self.flushCommands()

	def getForceLevel(self):
		return self.forceLevel

	def printWarning(self, message, newline=True):
		if self.verbose >= 0:
			self.flushCommands()
			if newline:
				print message
			else:
				sys.stdout.write(message)
				sys.stdout.flush()

	def printInfo(self, message, newline=True):
		if self.verbose >= 1:
			self.flushCommands()
			if newline:
				print message
			else:
				sys.stdout.write(message)
				sys.stdout.flush()

	def printDebug(self, message, newline=True):
		if self.verbose >= 2:
			self.flushCommands()
			if newline:
				print message
			else:
				sys.stdout.write(message)
				sys.stdout.flush()

	@staticmethod
	def __isTOP(usbdev):
		ids = ( (0x2471, 0x0853), )
		return (usbdev.idVendor, usbdev.idProduct) in ids

	def __initializeHardware(self):
		"Initialize the hardware"
		ver = self.cmdRequestVersion()
		self.printInfo("Initializing the '" + ver + "'...")

		self.queueCommand("\x0D")
		stat = self.cmdReadStatusReg32()
		if stat != 0x00020C69:
			raise TOPException("Init: Unexpected status register (a): 0x%08X" % stat)

		self.cmdFPGAWrite(0x1B, 0xFF)
		self.cmdSetVPPVoltage(0)
		self.cmdSetVPPVoltage(0)
		self.cmdSetVPPVoltage(0)
		self.cmdSetVPPVoltage(12)
		self.queueCommand("\x0E\x20\x00\x00")
		self.cmdFlush()
		self.cmdSetVCCXVoltage(0)
		self.cmdFPGAWrite(0x1D, 0x86)
		self.cmdLoadGNDLayout(0)
		self.cmdLoadVPPLayout(0)
		self.cmdLoadVCCXLayout(0)
		self.cmdSetVPPVoltage(0)
		self.cmdSetVPPVoltage(12)
		self.queueCommand("\x0E\x20\x00\x00")
		self.cmdFlush()
		self.queueCommand("\x0E\x25\x00\x00")
		stat = self.cmdReadStatusReg32()
		if stat != 0x0000686C:
			raise TOPException("Init: Unexpected status register (b): 0x%08X" % stat)

		self.__bitfileUpload()
		self.chip.initializeChip()

	def __bitfileUpload(self):
		self.printDebug("Uploading bitfile %s..." % self.bitfile.getFilename())

		self.cmdFPGAWrite(0x1B, 0x00)
		self.cmdFPGAInitiateConfig()
		stat = self.cmdReadStatusReg32()
		if stat != 0x00006801:
			raise TOPException("bit-upload: Failed to initiate " +\
				"config sequence (0x%08X)" % stat)

		data = self.bitfile.getPayload()
		for i in range(0, len(data), 60):
			self.cmdFPGAUploadConfig(data[i : i + 60])
		self.flushCommands()

	def readSignature(self):
		"""Reads the device signature and returns it."""
		self.printDebug("Reading signature from chip...")
		sig = self.chip.readSignature()
		self.printDebug("Done reading %d bytes." % len(sig))
		return sig

	def eraseChip(self):
		"""Erase the chip."""
		self.printDebug("Erasing chip...")
		self.chip.erase()

	def readProgmem(self):
		"""Reads the program memory image and returns it."""
		self.printDebug("Reading program memory from chip...")
		image = self.chip.readProgmem()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeProgmem(self, image):
		"""Writes a program memory image to the chip."""
		self.printDebug("Writing %d bytes of program memory to chip..." % len(image))
		self.chip.writeProgmem(image)
		self.printDebug("Done writing image.")

	def readEEPROM(self):
		"""Reads the EEPROM image and returns it."""
		self.printDebug("Reading EEPROM from chip...")
		image = self.chip.readEEPROM()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeEEPROM(self, image):
		"""Writes an EEPROM image to the chip."""
		self.printDebug("Writing %d bytes of EEPROM to chip..." % len(image))
		self.chip.writeEEPROM(image)
		self.printDebug("Done writing image.")

	def readFuse(self):
		"""Reads the fuses image and returns it."""
		self.printDebug("Reading fuses from chip...")
		image = self.chip.readFuse()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeFuse(self, image):
		"""Writes a fuses image to the chip."""
		self.printDebug("Writing %d bytes of fuses to chip..." % len(image))
		self.chip.writeFuse(image)
		self.printDebug("Done writing image.")

	def readLockbits(self):
		"""Reads the Lock bits image and returns it."""
		self.printDebug("Reading lock-bits from chip...")
		image = self.chip.readLockbits()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeLockbits(self, image):
		"""Writes a Lock bits image to the chip."""
		self.printDebug("Writing %d bytes of lock-bits to chip..." % len(image))
		self.chip.writeLockbits(image)
		self.printDebug("Done writing image.")

	def printZIFLayout(self):
		"""Prints the required ZIF layout."""
		print self.chip.generator.zifLayoutAsciiArt()

	def cmdFlush(self, count=1):
		"""Send 'count' flush requests."""
		assert(count >= 1)
		self.flushCommands()
		self.queueCommand(chr(0x1B) * count)
		self.flushCommands()

	def cmdReadStatusReg(self):
		"""Read the status register. Returns 64 bytes."""
		self.queueCommand(chr(0x07))
		return self.receive(64)

	def cmdReadStatusReg32(self):
		"""Read a 32bit value from the status register."""
		stat = self.cmdReadStatusReg()
		stat = ord(stat[0]) | (ord(stat[1]) << 8) | \
		       (ord(stat[2]) << 16) | (ord(stat[3]) << 24)
		return stat

	def cmdReadStatusReg48(self):
		"""Read a 48bit value from the status register."""
		stat = self.cmdReadStatusReg()
		stat = ord(stat[0]) | (ord(stat[1]) << 8) | \
		       (ord(stat[2]) << 16) | (ord(stat[3]) << 24) | \
		       (ord(stat[4]) << 32) | (ord(stat[5]) << 40)
		return stat

	def cmdRequestVersion(self):
		"""Returns the device ID and versioning string."""
		self.queueCommand("\x0E\x11\x00\x00")
		data = self.cmdReadStatusReg()
		return data[0:16].strip()

	def cmdFPGAInitiateConfig(self):
		"""Initiate a configuration sequence on the FPGA."""
		self.queueCommand("\x0E\x21\x00\x00")

	def cmdFPGAUploadConfig(self, data):
		"""Upload configuration data into the FPGA."""
		assert(len(data) <= 60)
		cmd = "\x0E\x22\x00\x00" + data
		cmd += "\x00" * (64 - len(cmd)) # padding
		self.queueCommand(cmd)

	def cmdFPGAReadByte(self):
		"""Read a byte from the FPGA data line into the status register."""
		self.queueCommand("\x01")

	def cmdFPGAReadRaw(self, address):
		"""Read a byte from the FPGA at address into the status register."""
		cmd = chr(0x0B) + chr(address)
		self.queueCommand(cmd)

	def cmdFPGAWrite(self, address, byte):
		"""Write a byte to an FPGA address."""
		cmd = chr(0x0A) + chr(address) + chr(byte)
		self.queueCommand(cmd)

	def cmdLoadGNDLayout(self, layout):
		"""Load the GND configuration into the H/L shiftregisters."""
		cmd = chr(0x0E) + chr(0x16) + chr(layout) + chr(0)
		self.queueCommand(cmd)
		self.delay(0.15)
		self.cmdFlush()

	def cmdSetVPPVoltage(self, voltage):
		"""Set the VPP voltage. voltage is a floating point voltage number."""
		centivolt = int(voltage * 10)
		cmd = chr(0x0E) + chr(0x12) + chr(centivolt) + chr(0)
		self.queueCommand(cmd)
		self.cmdFlush()

	def cmdLoadVPPLayout(self, layout):
		"""Load the VPP configuration into the shift registers."""
		cmd = chr(0x0E) + chr(0x14) + chr(layout) + chr(0)
		self.queueCommand(cmd)
		self.delay(0.15)
		self.cmdFlush()

	def cmdSetVCCXVoltage(self, voltage):
		"""Set the VCCX voltage. voltage is a floating point voltage number."""
		centivolt = int(voltage * 10)
		cmd = chr(0x0E) + chr(0x13) + chr(centivolt) + chr(0)
		self.queueCommand(cmd)
		self.cmdFlush()

	def cmdLoadVCCXLayout(self, layout):
		"""Load the VCCX configuration into the shift registers."""
		cmd = chr(0x0E) + chr(0x15) + chr(layout) + chr(0)
		self.queueCommand(cmd)
		self.delay(0.15)
		self.cmdFlush()

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
			if len(self.commandQueue) >= 128:
				self.flushCommands()

	def receive(self, size):
		"""Receive 'size' bytes on the bulk-in ep."""
		# If there are blocked commands in the queue, send them now.
		self.flushCommands()
		try:
			ep = self.bulkIn.address
			data = ""
			for c in self.usbh.bulkRead(ep, size):
				data += chr(c)
			if self.verbose >= 3:
				print "Received data:"
				dumpMem(data)
		except (usb.USBError), e:
			raise TOPException("USB bulk read error: " + str(e))
		return data

	def flushCommands(self):
		"""Flush the command queue, but don't unblock it."""
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

	def delay(self, seconds):
		"""Flush all commands and delay for 'seconds'"""
		self.flushCommands()
		time.sleep(seconds)
