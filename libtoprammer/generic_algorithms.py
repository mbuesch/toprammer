"""
#    TOP2049 Open Source programming suite
#
#    Generic programming algorithms
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

from .util import *


class AddrSetter(object):
	"""Generic address setter"""

	def __init__(self, chip,
		     fpgaCmdByte0,
		     fpgaCmdByte1 = -1,
		     fpgaCmdByte2 = -1,
		     fpgaCmdByte3 = -1,
		     addrSetupFunc = lambda byteNr, data: None,
		     addrFinishFunc = lambda byteNr, data: None):
		"""
		chip => The Chip.
		fpgaCmdByte0 => FPGA command number for setting addr byte 0.
		fpgaCmdByte1 => FPGA command number for setting addr byte 1.
		fpgaCmdByte2 => FPGA command number for setting addr byte 2.
		fpgaCmdByte3 => FPGA command number for setting addr byte 3.
		addrSetupFunc => Optional function called before addr write.
		addrFinishFunc => Optional function called after addr write.
		"""
		self.chip = chip
		self.fpgaCmds = [
			fpgaCmdByte0,
			fpgaCmdByte1,
			fpgaCmdByte2,
			fpgaCmdByte3,
		]
		self.addrSetupFunc = addrSetupFunc
		self.addrFinishFunc = addrFinishFunc
		self.reset()

	def reset(self):
		self.prevAddr = None

	def load(self, addr):
		"""Load an address into the FPGA.
		This loads only the bytes that changed."""
		shifts = (0, 8, 16, 24)
		for byteNr, shift in enumerate(shifts):
			fpgaCmd = self.fpgaCmds[byteNr]
			if fpgaCmd < 0:
				continue
			addrByte = (addr >> shift) & 0xFF
			if self.prevAddr is None or\
			   ((self.prevAddr >> shift) & 0xFF) != addrByte:
				self.addrSetupFunc(byteNr, addrByte)
				self.chip.top.cmdFPGAWrite(fpgaCmd, addrByte)
				self.addrFinishFunc(byteNr, addrByte)
		self.prevAddr = addr

class GenericAlgorithms(object):
	"""Generic programming algorithms."""

	def __init__(self, chip):
		self.chip = chip

	def simpleVoltageSetup(self, vcc=5.0, vpp=5.0, vppEnable=False):
		"""Simple voltage setup."""
		self.chip.top.cmdSetVCCVoltage(vcc)
		self.chip.top.cmdSetVPPVoltage(vpp)
		self.chip.applyVCC(True)
		self.chip.applyGND(True)
		self.chip.applyVPP(vppEnable)

	def simpleVoltageShutdown(self):
		"""Turn off voltages."""
		self.chip.applyVCC(False)
		self.chip.applyVPP(False)
		self.chip.applyGND(False)
		self.chip.top.cmdSetVCCVoltage(self.chip.top.vcc.minVoltage())
		self.chip.top.cmdSetVPPVoltage(self.chip.top.vpp.minVoltage())

	def simpleRead(self, name, sizeBytes,
		       readData8Func,
		       addrSetter,
		       initFunc = lambda: None,
		       exitFunc = lambda: None):
		"""Simple 8-bit data read algorithm."""
		self.chip.progressMeterInit("Reading %s" % name, sizeBytes)
		image, count = [], 0
		initFunc()
		addrSetter.reset()
		for addr in range(0, sizeBytes):
			self.chip.progressMeter(addr)
			addrSetter.load(addr)
			readData8Func()
			count += 1
			if count == self.chip.top.getBufferRegSize():
				image.append(self.chip.top.cmdReadBufferReg())
				count = 0
		if count:
			image.append(self.chip.top.cmdReadBufferReg()[:count])
		exitFunc()
		self.chip.progressMeterFinish()
		return b"".join(image)

	def simpleReadEPROM(self, sizeBytes,
			    readData8Func,
			    addrSetter,
			    initFunc = lambda: None,
			    exitFunc = lambda: None):
		return self.simpleRead("EPROM", sizeBytes, readData8Func,
				       addrSetter, initFunc, exitFunc)

	def simpleReadEEPROM(self, sizeBytes,
			     readData8Func,
			     addrSetter,
			     initFunc = lambda: None,
			     exitFunc = lambda: None):
		return self.simpleRead("EEPROM", sizeBytes, readData8Func,
				       addrSetter, initFunc, exitFunc)

	def simpleTest(self, readFunc, writeFunc, size):
		"""Simple Unit-test."""
		image = genRandomBlob(size)
		writeFunc(image)
		if readFunc() != image:
			self.chip.throwError("Unit-test failed. "
				"The chip may be physically broken.")
