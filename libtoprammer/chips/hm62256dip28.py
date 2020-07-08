"""
#    TOP2049 Open Source programming suite
#
#    HM62256 DIP28 SRAM support
#
#    Copyright (c) 2011 Michael Buesch <m@bues.ch>
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

from .generic_sram import *


class Chip_HM62256DIP28(Chip_genericSRAM):
	def __init__(self):
		Chip_genericSRAM.__init__(self,
			chipPackage = "DIP28",
			chipPinVCC = 28,
			chipPinGND = 14,
			VCCVoltage = 5,
			nrAddressBits = 15,
			nrDataBits = 8,
		)

ChipDescription(
	Chip_HM62256DIP28,
	bitfile = "hm62256dip28",
	runtimeID = (0x000A, 0x01),
	chipType = ChipDescription.TYPE_SRAM,
	chipVendors = "S@Tech",
	description = "HM62256 SRAM",
	packages = ( ("DIP28", ""), )
)
