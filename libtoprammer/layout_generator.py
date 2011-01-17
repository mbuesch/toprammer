"""
#    TOP2049 Open Source programming suite
#
#    ZIF socket layout generator
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

from util import *
from top_xxxx import *


class LayoutGenerator:
	"Layout generator baseclass."

	class MapError(Exception): pass

	def __init__(self):
		pass

	def setProgrammerType(self, programmer="TOP2049"):
		supportedDevices = {
			# Map  deviceName : layoutModules, ZIF-pin-count
			"TOP2049"	: (top2049.vccx_layouts, top2049.vpp_layouts,
					   top2049.gnd_layouts, 48)
		}
		try:
			(vccx_layouts, vpp_layouts, gnd_layouts, zifPins) = \
				supportedDevices[programmer.upper()]
		except (KeyError), e:
			raise TOPException("Programmer " + programmer + " not supported")
		self.vccxLayout = vccx_layouts.VCCXLayout()
		self.vppLayout = vpp_layouts.VPPLayout()
		self.gndLayout = gnd_layouts.GNDLayout()
		self.zifPins = zifPins

	def setPins(self, vccxPin, vppPins, gndPin):
		"""Load the supply pin locations.
		vppPins may either be one pin number or a list of pin numbers or None."""
		self.vccxPin = vccxPin
		if vppPins is None:
			self.vppPins = None
		else:
			try:
				self.vppPins = list(vppPins)
			except TypeError:
				self.vppPins = [ vppPins, ]
		self.gndPin = gndPin
		self.verifyPins()

	def verifyPins(self):
		pass

	def maxOffset(self, upsideDown):
		"Returns the max possible chip offset (in the ZIF socket)"
		raise TOPException("Reimplement me")

	def mapToZIF(self, offset, upsideDown):
		"Tries to map the chip into the ZIF socket"
		if offset < 0 or offset > self.maxOffset(upsideDown):
			raise self.MapError()

		# Find a GND layout
		zifGndPin = self.mapPin2zif(self.gndPin, offset, upsideDown)
		self.result_GND = self.__findSingleLayout(
					self.gndLayout,
					(1 << (zifGndPin - 1)))

		# Find a VCCX layout
		zifVccxPin = self.mapPin2zif(self.vccxPin, offset, upsideDown)
		self.result_VCCX = self.__findSingleLayout(
					self.vccxLayout,
					(1 << (zifVccxPin - 1)))

		# Find a (possibly cumulative) VPP layout
		if self.vppPins is None:
			self.result_VPP = None
		else:
			zifVppMask = 0
			for vppPin in self.vppPins:
				pin = self.mapPin2zif(vppPin, offset, upsideDown)
				zifVppMask |= (1 << (pin - 1))
			self.result_VPP = self.__findCumulativeLayout(
						self.vppLayout,
						zifVppMask)

		# Also store the chip orientation for later use.
		self.result_upsideDown = upsideDown
		self.result_offset = offset

	def mapPin2zif(self, packagePin, offset, upsideDown):
		"Map a package pin to a ZIF pin. Returns the ZIF pin number."
		raise TOPException("Reimplement me")

	def zifLayoutAsciiArt(self):
		"Returns nice ascii ART of the mapped ZIF socket"
		raise TOPException("Reimplement me")

	def zifPinAssignments(self):
		"Returns a string describing the pin assignments"
		vccx = str(self.__bitmask2pinList(self.result_VCCX[1])).strip("[]")
		ret =  "VCCX ZIF pins: " + vccx + "\n"
		if self.result_VPP:
			vppBitmask = 0
			for (id, mask) in self.result_VPP:
				vppBitmask |= mask
			vpp = str(self.__bitmask2pinList(vppBitmask)).strip("[]")
			ret += "VPP ZIF pins:  " + vpp + "\n"
		gnd = str(self.__bitmask2pinList(self.result_GND[1])).strip("[]")
		ret += "GND ZIF pins:  " + gnd + "\n"
		return ret

	def __bitmask2pinList(self, bitmask):
		ret = []
		bit = 0
		while bitmask:
			if bitmask & (1 << bit):
				ret.append(bit + 1)
			bitmask &= ~(1 << bit)
			bit += 1
		return ret

	def __pinList2Bitmask(self, pinList):
		bitmask = 0
		for pin in pinList:
			assert(pin >= 1)
			bitmask |= (1 << (pin - 1))
		return bitmask

	def recalculate(self):
		"Redo the mapping calculation"
		for upsideDown in (False, True):
			offset = self.maxOffset(upsideDown)
			while offset >= 0:
				try:
					self.mapToZIF(offset, upsideDown)
				except (LayoutGenerator.MapError), e:
					offset -= 1
					continue
				return
		raise TOPException("Did not find a possible valid layout for the setup")

	def applyGNDLayout(self, top):
		"Send the GND layout to hardware"
		(id, mask) = self.result_GND
		top.gnd.setLayoutID(id)

	def applyVCCXLayout(self, top):
		"Send the VCCX layout to hardware"
		(id, mask) = self.result_VCCX
		top.vccx.setLayoutID(id)

	def applyVPPLayout(self, top, packagePins=[]):
		"""Send the VPP layout to hardware.
		packagePins is a list of pins (on the chip package) to activate.
		If packagePins is not passed, all VPP pins are driven to VPP."""
		if packagePins:
			pins = []
			for pin in packagePins:
				pins.append(self.mapPin2zif(pin, self.result_offset,
							    self.result_upsideDown))
			packagePinsMask = self.__pinList2Bitmask(pins)
		top.vpp.setLayoutMask(0) # Reset
		if self.result_VPP:
			for (id, mask) in self.result_VPP:
				if packagePins:
					if mask & packagePinsMask == 0:
						continue
					if mask & packagePinsMask != mask:
						raise TOPException(
							"Unable to apply partial VPP layout")
				top.vpp.setLayoutID(id)

	def __findSingleLayout(self, layoutDefs, zifBitmask):
		# Returns an (id, mask) tuple
		for (id, mask) in layoutDefs.supportedLayouts():
			if zifBitmask == mask:
				break
		else:
			raise self.MapError()
		return (id, mask)

	def __findCumulativeLayout(self, layoutDefs, zifBitmask):
		# Returns a list of (id, mask) tuples
		result = []
		for (id, mask) in layoutDefs.supportedLayouts():
			if zifBitmask == 0:
				break
			if mask == 0:
				continue
			if mask & zifBitmask == mask:
				result.append( (id, mask) )
				zifBitmask &= ~mask
		if zifBitmask:
			raise self.MapError()
		return result

class LayoutGeneratorDIP(LayoutGenerator):
	"Layout generator for DIP packages."

	def __init__(self, nrPins):
		LayoutGenerator.__init__(self)
		self.nrPins = nrPins

	def verifyPins(self):
		LayoutGenerator.verifyPins(self)
		if self.nrPins < 2 or self.nrPins > self.zifPins or self.nrPins % 2 != 0:
			raise TOPException("Invalid DIP package")
		if self.vccxPin < 1 or self.vccxPin > self.nrPins:
			raise TOPException("Invalid VCCX pin number for the selected package")
		if self.vppPins is not None:
			for vppPin in self.vppPins:
				if vppPin < 1 or vppPin > self.nrPins:
					raise TOPException("Invalid VPP pin number for the selected package")
		if self.gndPin < 1 or self.gndPin > self.nrPins:
			raise TOPException("Invalid GND pin number for the selected package")

	def maxOffset(self, upsideDown):
		return self.zifPins // 2 - self.nrPins // 2

	def mapPin2zif(self, dipPin, offset, upsideDown):
		if upsideDown:
			if dipPin > self.nrPins // 2:
				# Right side of DIP
				dipPin -= self.nrPins // 2
				return dipPin + offset
			else:
				# Left side of DIP
				return self.zifPins - self.nrPins // 2 + dipPin - offset
		else:
			if dipPin > self.nrPins // 2:
				# Right side of DIP
				dipPin -= self.nrPins // 2
				return self.zifPins - self.nrPins // 2 + dipPin - offset
			else:
				# Left side of DIP
				return dipPin + offset

	def zifLayoutAsciiArt(self):
		ret =  "T     ZIF socket\n"
		ret += "^--o==============o\n"
		for zp in range(1, self.zifPins // 2 + 1):
			if zp < self.result_offset + 1 or \
			   zp > self.result_offset + self.nrPins // 2:
				ret += "%2d |----- || -----| %2d\n" %\
					(zp, self.zifPins + 1 - zp)
			else:
				if zp == self.result_offset + 1 and \
				   not self.result_upsideDown:
					ret += "%2d |-- 1##..##o --| %2d\n" %\
						(zp, self.zifPins + 1 - zp)
				elif zp == self.result_offset + self.nrPins // 2 and \
				     self.result_upsideDown:
					ret += "%2d |-- o##''##1 --| %2d\n" %\
						(zp, self.zifPins + 1 - zp)
				else:
					ret += "%2d |-- o######o --| %2d\n" %\
						(zp, self.zifPins + 1 - zp)
		ret += "   o==============o"
		return ret

def createLayoutGenerator(package):
	try:
		for regex in ("DIP(\d+)", "PDIP(\d+)", "SO(\d+)", "TSSOP(\d+)", ):
			m = re.match(regex, package, re.IGNORECASE)
			if m:
				nrPins = int(m.group(1))
				return LayoutGeneratorDIP(nrPins)
		if package.upper() == "PLCC32": # 1:1 adapter
			return LayoutGeneratorDIP(32)
		if package.upper() == "PLCC44": # 1:1 adapter
			return LayoutGeneratorDIP(44)
		raise ValueError()
	except (ValueError), e:
		raise TOPException("Unknown package type " + package)
