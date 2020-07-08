"""
#    TOP2049 Open Source programming suite
#
#    TOP2049 VCC layout definitions
#
#    Copyright (c) 2010 Michael Buesch <m@bues.ch>
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
if __name__ == "__main__":
	sys.path.insert(0, sys.path[0] + "/../..")
from libtoprammer.shiftreg_layout import *


class VCCLayout(ShiftregLayout):
	# "shiftreg_masks" is a dump of the VCC shiftregister states. The array index
	# is the layout ID and the array entries are the inverted shift
	# register outputs. The least significant byte is the first
	# shift register in the chain.
	shiftreg_masks = (
		0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		0x000000, 0x000000, 0x000001, 0x000000, 0x000000, 0x002000,
		0x000000, 0x000002, 0x000000, 0x000000, 0x080000, 0x000004,
		0x000000, 0x000000, 0x010000, 0x004000, 0x000000, 0x000000,
		0x000008, 0x000010, 0x000020, 0x000040, 0x000080, 0x000000,
		0x000100, 0x000000, 0x000200, 0x000000, 0x000400, 0x000000,
		0x000800, 0x000000, 0x008000, 0x000000, 0x001000, 0x000000,
		0x020000, 0x000000, 0x040000, #0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x012000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000, 0x000000, 0x000000,
		#0x000000, 0x000000, 0x000000, 0x000000,
	)
	# "shreg2zif_map" is a mapping of the shift register outputs
	# to the ZIF socket pins
	shreg2zif_map = {
		# SHREG.PIN  :  ZIF_PIN

		# left side
		# 1
		# 2
		# 3
		# 4
		# 5
		# 6
		# 7
		# 8
		# 9
		# 10
		# 11
		"0.0" : 12,	# Q8C
		# 13
		# 14
		"1.5" : 15,	# Q11C
		# 16
		"0.1" : 17,	# Q13C
		# 18
		# 19
		"2.3" : 20,	# Q16C
		"0.2" : 21,	# Q17C
		# 22
		# 23
		"2.0" : 24,	# Q20C

		# right side
		"2.2" : 48,	# Q44C
		# 47		
		"2.1" : 46,	# Q42C
		# 45		
		"1.4" : 44,	# Q40C
		# 43		
		"1.7" : 42,	# Q38C
		# 41		
		"1.3" : 40,	# Q36C
		# 39		
		"1.2" : 38,	# Q34C
		# 37		
		"1.1" : 36,	# Q32C
		# 35		
		"1.0" : 34,	# Q30C
		# 33		
		"0.7" : 32,	# Q28C
		"0.6" : 31,	# Q27C
		"0.5" : 30,	# Q26C
		"0.4" : 29,	# Q25C
		"0.3" : 28,	# Q24C
		# 27		
		# 26		
		"1.6" : 25,	# Q21C
	}

	def __init__(self, top=None):
		ShiftregLayout.__init__(self, nrZifPins=48, nrShiftRegs=3)
		self.top = top

	def minVoltage(self):
		"Get the min supported voltage"
		return 3

	def maxVoltage(self):
		"Get the max supported voltage"
		return 5

	def setLayoutID(self, id):
		self.top.cmdLoadVCCLayout(id)

if __name__ == "__main__":
	print("ZIF socket VCC layouts")
	print(VCCLayout())
