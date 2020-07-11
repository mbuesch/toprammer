"""
#    TOP2049 Open Source programming suite
#
#    Atmel Tiny25 DIP8
#
#    Copyright (c) 2020 Michael Buesch <m@bues.ch>
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

from libtoprammer.chips.attinyspc_common import *


class Chip_AtTiny25dip8(Chip_AtTinySPC_common):
	def __init__(self):
		Chip_AtTinySPC_common.__init__(self,
			chipPackage="DIP8",
			chipPinVCC=8,
			chipPinsVPP=1,
			chipPinGND=4,
			signature=b"\x1E\x91\x08",
			flashPageSize=16,
			flashPages=64,
			eepromPageSize=4,
			eepromPages=32,
			nrFuseBits=17,
			nrLockBits=2,
		)

ChipDescription(
	Chip_AtTiny25dip8,
	chipID="attiny25dip8",
	bitfile="attiny13dip8",
	runtimeID=(0x0001, 0x01),
	chipVendors="Atmel",
	description="AtTiny25",
	packages=( ("DIP8", ""), ),
)
