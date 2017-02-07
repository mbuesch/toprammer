"""
#    TOP2049 Open Source programming suite
#
#    Copyright (c) 2009-2017 Michael Buesch <m@bues.ch>
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

import sys
__pymajor = sys.version_info[0]
__pyminor = sys.version_info[1]
if __pymajor < 2 or (__pymajor == 2 and __pyminor < 6):
	print "FATAL: TOPrammer requires Python version 2.6. Please install Python 2.6"
	sys.exit(1)


# TOPrammer version stamp
VERSION_MAJOR	= 0
VERSION_MINOR	= 17
VERSION = "%d.%d" % (VERSION_MAJOR, VERSION_MINOR)


from bitfile import *
from util import *

import time
import re

from hardware_access_usb import *
from top_devices import *
from chips import *
from user_interface import *


class FoundDev(object):
	def __init__(self, toptype, devIdentifier, busdata=None):
		self.toptype = toptype
		self.devIdentifier = devIdentifier
		self.busdata = busdata

class TOP(object):
	# Supported programmer types
	TYPE_TOP2049		= "TOP2049"

	def __init__(self, devIdentifier=None, verbose=0,
		     forceLevel=0, noqueue=False, usebroken=False,
		     forceBitfileUpload=False,
		     userInterface=ConsoleUserInterface()):

		self.verbose = verbose
		self.forceLevel = forceLevel
		self.forceBitfileUpload = forceBitfileUpload
		self.usebroken = usebroken
		self.userInterface = userInterface

		self.hw = None
		self.chip = None

		# Find the device
		devices = self.findDevices()
		if devIdentifier:
			devices = [ d for d in devices
				    if d.devIdentifier.lower() == devIdentifier.lower() ]
		if not devices:
			raise TOPException("TOP programmer device not found!")
		foundDev = devices[0] # Select first

		if noqueue:
			self.printWarning("WARNING: Command queuing disabled. " +\
				"Hardware access will be _really_ slow.")

		self.initializeProgrammer(foundDev, noqueue)

	def getProgrammerType(self):
		"Returns the TYPE_TOPxxxx"
		return self.topType

	def initializeChip(self, chipID, assignedChipOptions=()):
		"Initialize the programmer for a chip"
		# If a chip is initialized, shut it down first.
		if self.chip:
			self.shutdownChip()
		# Find the implementation of the chip.
		descriptor = ChipDescription.findOne(chipID, self.usebroken)
		self.chip = descriptor.chipImplClass.createInstance(
			top = self,
			chipDescription = descriptor,
			assignedChipOptions = assignedChipOptions)
		ok = self.configureFPGA(descriptor.bitfile, descriptor.runtimeID)
		if not ok:
			self.chip = None
			raise TOPException("Did not find BIT-file for chip implementation %s" % chipID)

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

	@classmethod
	def __usbdev2toptype(cls, usbdev):
		"Returns the TOP type of the USB device. None, if this is not a TOP device."
		try:
			toptype = {
				(0x2471, 0x0853):	TOP.TYPE_TOP2049,
			}[ (usbdev.idVendor, usbdev.idProduct) ]
		except (KeyError), e:
			return None
		return toptype

	@classmethod
	def findDevices(cls):
		"""Rescan all busses for TOP devices.
		Returns a list of FoundDev()"""
		usbFound = HardwareAccessUSB.scan(cls.__usbdev2toptype)
		devices = []
		for i, ud in enumerate(usbFound):
			toptype = cls.__usbdev2toptype(ud.usbdev)
			devices.append(
				FoundDev(toptype,
					 "usb:%s:%d" % (toptype, i),
					 ud)
			)
		return devices

	def initializeProgrammer(self, foundDev, noQueue):
		"Initialize the hardware"

		self.shutdownProgrammer()

		if foundDev.toptype == self.TYPE_TOP2049:
			self.hw = top2049.hardware_access.HardwareAccess(
					foundUSBDev = foundDev.busdata,
					noQueue = noQueue,
					doRawDump = (self.verbose >= 3))
			self.vcc = top2049.vcc_layouts.VCCLayout(self)
			self.vpp = top2049.vpp_layouts.VPPLayout(self)
			self.gnd = top2049.gnd_layouts.GNDLayout(self)
		else:
			assert(0)
		self.topType = foundDev.toptype

		versionRegex = (
			(r"top2049\s+ver\s*(\d+\.\d+)", self.TYPE_TOP2049),
		)

		# This is the first hardware access. Try several times since the programmer is in an unknown state.
		for _ in range(5):
			try:
				versionString = self.hw.readVersionString()
				break
			except TOPException, e:
				time.sleep(0.05)
		else:
			raise TOPException("Could not read version string from hardware")
		for (regex, t) in versionRegex:
			if t != self.topType:
				continue
			m = re.match(regex, versionString, re.IGNORECASE)
			if m:
				self.topVersion = m.group(1)
				break
		else:
			raise TOPException("Connected TOP programmer '" + versionString +\
				"' is not supported by Toprammer, yet")
		self.printInfo("Initializing the " + self.topType + " version " + self.topVersion)

		self.hw.hardwareInit()

	def shutdownProgrammer(self):
		if self.hw:
			self.hw.shutdown()
		self.hw = None
		self.topType = None
		self.topVersion = None

	def __readBitfileID(self):
		self.cmdFPGARead(0xFD)
		self.cmdFPGARead(0xFE)
		self.cmdFPGARead(0xFF)
		data = self.cmdReadBufferReg(3)
		gotID = byte2int(data[0]) | (byte2int(data[1]) << 8)
		if gotID == 0xFEFD or gotID == 0xFFFF:
			gotID = 0
		gotRev = byte2int(data[2])
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

		self.hw.FPGAInitiateConfig()
		data = self.bitfile.getPayload()
		chunksz = self.hw.getFPGAMaxConfigChunkSize()
		chunksz = chunksz if chunksz > 0 else len(data)
		for i in range(0, len(data), chunksz):
			self.hw.FPGAUploadConfig(i, data[i : i + chunksz])
		self.flushCommands()

		if requiredID and requiredRevision:
			# Check the uploaded ID
			(gotID, gotRev) = self.__readBitfileID()
			if gotID != requiredID or gotRev != requiredRevision:
				raise TOPException("bit-upload: The bitfile upload succeed, "
					"but the read ID or revision is invalid. "
					"(Got 0x%04X/0x%02X, but expected 0x%04X/0x%02X)" %\
					(gotID, gotRev, requiredID, requiredRevision))

	def configureFPGA(self, bitfileName, runtimeIDs):
		"""Upload and configure the FPGA.
		bitfileName -> The name of the bitfile to upload
		runtimeIDs -> bottom-half ID tuple: (majorID, minorID)"""
		# Get the bitfile path.
		bitfilePath = bitfileFind(bitfileName)
		if not bitfilePath:
			return False
		# Open and parse the bitfile.
		self.bitfile = Bitfile()
		self.bitfile.parseFile(bitfilePath)
		# Initialize the hardware.
		self.__bitfileUpload(runtimeIDs)
		return True

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
		
	def readUserIdLocation(self):
		"""Reads the User ID Location and returns it."""
		self.printDebug("Reading UIL from chip...")
		self.checkChip()
		image = self.chip.readUserIdLocation()
		self.flushCommands()
		self.printDebug("Done reading %d bytes." % len(image))
		return image

	def writeUserIdLocation(self, image):
		"""Writes the User ID Location image to the chip."""
		self.printDebug("Writing %d bytes to UIL of the chip..." % len(image))
		self.checkChip()
		self.chip.writeUserIdLocation(image)
		self.flushCommands()
		self.printDebug("Done writing the image.")		

	def cmdDelay(self, seconds):
		"""Send a delay request to the device. Note that this causes the
		programmer to execute the delay. For a host-delay, use hostDelay()"""
		self.hw.delay(seconds)

	def hostDelay(self, seconds):
		"""Flush all commands and delay the host computer for 'seconds'"""
		self.flushCommands(seconds)

	def getOscillatorHz(self):
		"""Returns the FPGA oscillator frequency, in Hz.
		The oscillator is connected to the FPGA clk pin."""
		return self.hw.getOscillatorHz()

	def getBufferRegSize(self):
		"""Returns the size (in bytes) of the buffer register."""
		return self.hw.getBufferRegSize()

	def cmdReadBufferReg(self, nrBytes=-1):
		"""Read the buffer register. Returns nrBytes (default all bytes)."""
		regSize = self.getBufferRegSize()
		if nrBytes < 0:
			nrBytes = regSize
		assert(nrBytes <= regSize)
		if not nrBytes:
			return b""
		return self.hw.readBufferReg(nrBytes)

	def cmdReadBufferReg8(self):
		"""Read a 8bit value from the buffer register."""
		stat = self.cmdReadBufferReg(1)
		stat = byte2int(stat[0])
		return stat

	def cmdReadBufferReg16(self):
		"""Read a 16bit value from the buffer register."""
		stat = self.cmdReadBufferReg(2)
		stat = byte2int(stat[0]) | (byte2int(stat[1]) << 8)
		return stat

	def cmdReadBufferReg24(self):
		"""Read a 24bit value from the buffer register."""
		stat = self.cmdReadBufferReg(3)
		stat = byte2int(stat[0]) | (byte2int(stat[1]) << 8) | (byte2int(stat[2]) << 16)
		return stat

	def cmdReadBufferReg32(self):
		"""Read a 32bit value from the buffer register."""
		stat = self.cmdReadBufferReg(4)
		stat = byte2int(stat[0]) | (byte2int(stat[1]) << 8) | \
		       (byte2int(stat[2]) << 16) | (byte2int(stat[3]) << 24)
		return stat

	def cmdReadBufferReg48(self):
		"""Read a 48bit value from the buffer register."""
		stat = self.cmdReadBufferReg(6)
		stat = byte2int(stat[0]) | (byte2int(stat[1]) << 8) | \
		       (byte2int(stat[2]) << 16) | (byte2int(stat[3]) << 24) | \
		       (byte2int(stat[4]) << 32) | (byte2int(stat[5]) << 40)
		return stat

	def cmdFPGARead(self, address):
		"""Read a byte from the FPGA at address into the buffer register."""
		self.hw.FPGARead(address)

	def cmdFPGAWrite(self, address, byte):
		"""Write a byte to an FPGA address."""
		return self.hw.FPGAWrite(address, byte)

	def cmdLoadGNDLayout(self, layout):
		"""Load the GND configuration into the programmer."""
		self.hw.loadGNDLayout(layout)

	def cmdSetVPPVoltage(self, voltage):
		"""Set the VPP voltage. voltage is a floating point voltage number."""
		self.hw.setVPPVoltage(voltage)

	def cmdLoadVPPLayout(self, layout):
		"""Load the VPP configuration into the programmer."""
		self.hw.loadVPPLayout(layout)

	def cmdSetVCCVoltage(self, voltage):
		"""Set the VCC voltage. voltage is a floating point voltage number."""
		self.hw.setVCCVoltage(voltage)

	def cmdLoadVCCLayout(self, layout):
		"""Load the VCC configuration into the shift registers."""
		self.hw.loadVCCLayout(layout)

	def cmdEnableZifPullups(self, enable):
		"""Enable the ZIF socket signal pullups."""
		self.hw.enableZifPullups(enable)

	def flushCommands(self, sleepSeconds=0):
		"""Flush command queue and optionally sleep for 'sleepSeconds'."""
		self.hw.flushCommands(sleepSeconds)
