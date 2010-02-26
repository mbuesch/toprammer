"""
#    TOP2049 Open Source programming suite
#
#    TOP2049 VPP layout definitions
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

import sys
if __name__ == "__main__":
	sys.path.insert(0, sys.path[0] + "/../..")
from libtoprammer.shiftreg_layout import *


class VPPLayout(ShiftregLayout):
	# "shiftreg_masks" is a dump of the VPP shiftregister states. The array index
	# is the layout ID and the array entries are the inverted shift
	# register outputs. The least significant byte is the first
	# shift register in the chain.
	shiftreg_masks = (
		0x00000000, 0x02000000, 0x03000000, 0x03000008, 0x03000008,
		0x03100008, 0x03100008, 0x03120008, 0x03130008, 0x03134008,
		0x03136008, 0x03137008, 0x03137208, 0x03137208, 0x03137308,
		0x03137328, 0x03137328, 0x03137328, 0x03137328, 0x03137328,
		0x03137329, 0x03137329, 0x0313732B, 0x0313732B, 0x0313732B,
		0x0313732B, 0x0313732F, 0x0313733F, 0x0313737F, 0x031373FF,
		0x031377FF, 0x03137FFF, 0x03137FFF, 0x0313FFFF, 0x0317FFFF,
		0x031FFFFF, 0x031FFFFF, 0x033FFFFF, 0x033FFFFF, 0x037FFFFF,
		0x03FFFFFF, 0x03FFFFFF, 0x07FFFFFF, 0x0FFFFFFF, 0x8FFFFFFF,
		0xCFFFFFFF, 0xEFFFFFFF, 0xFFFFFFFF, #0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
		#0xFFFFFFFF,
	)
	# "shreg2zif_map" is a mapping of the shift register outputs
	# to the ZIF socket pins
	shreg2zif_map = {
		# SHREG.PIN  :  ZIF_PIN

		# left side
		"3.6" : 1,	# QP31
		"3.5" : 2,	# QP30
		"3.4" : 3,	# QP29
		# 4
		"3.1" : 5,	# QP26
		"3.0" : 6,	# QP25
		"0.3" : 7,	# QP4
		# 8
		"2.4" : 9,	# QP21
		# 10
		"2.1" : 11,	# QP18
		"2.0" : 12,	# QP17
		"1.6" : 13,	# QP15
		"1.5" : 14,	# QP14
		"1.4" : 15,	# QP13
		"1.1" : 16,	# QP10
		# 17
		"1.0" : 18,	# QP9
		"0.5" : 19,	# QP6
		# 20
		# 21
		# 22
		# 23
		"0.0" : 24,	# QP1

		# right side
		"3.7" : 48,	# QP32	
		"3.3" : 47,	# QP28	
		"3.2" : 46,	# QP27	
		# 45		
		"2.7" : 44,	# QP24	
		"2.6" : 43,	# QP23	
		# 42		
		"2.5" : 41,	# QP22	
		# 40		
		"2.3" : 39,	# QP20	
		"2.2" : 38,	# QP19	
		"1.7" : 37,	# QP16	
		# 36		
		"1.3" : 35,	# QP12	
		"1.2" : 34,	# QP11	
		"0.7" : 33,	# QP8	
		"0.6" : 32,	# QP7	
		"0.4" : 31,	# QP5	
		"0.2" : 30,	# QP3	
		# 29		
		# 28		
		# 27		
		"0.1" : 26,	# QP2	
		# 25		
	}

	def __init__(self, top=None):
		ShiftregLayout.__init__(self, nrZifPins=48, nrShiftRegs=4)
		self.top = top

	def minVoltage(self):
		"Get the min supported voltage"
		return 5

	def maxVoltage(self):
		"Get the max supported voltage"
		return 21

	def setLayoutID(self, id):
		self.top.cmdLoadVPPLayout(id)

if __name__ == "__main__":
	print "ZIF socket VPP layouts"
	print VPPLayout(None)
