"""
#    TOP2049 Open Source programming suite
#
#    Utility functions
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

import sys


class TOPException(Exception): pass


def dumpMem(mem):
	def toAscii(char):
		if char >= 32 and char <= 126:
			return chr(char)
		return "."

	ascii = ""
	for i in range(0, len(mem)):
		if i % 16 == 0 and i != 0:
			sys.stdout.write("  " + ascii + "\n")
			ascii = ""
		if i % 16 == 0:
			sys.stdout.write("0x%04X:  " % i)
		c = ord(mem[i])
		sys.stdout.write("%02X" % c)
		if (i % 2 != 0):
			sys.stdout.write(" ")
		ascii += toAscii(c)
	sys.stdout.write("  " + ascii + "\n\n")
