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
import re


class TOPException(Exception): pass


hexdump_re = re.compile(r"0x[0-9a-fA-F]+:\s+([0-9a-fA-F\s]+)\s+.+")

def parseHexdump(dump):
	try:
		bin = []
		for line in dump.splitlines():
			line = line.strip()
			if not line:
				continue
			m = hexdump_re.match(line)
			if not m:
				raise TOPException("Invalid hexdump format (regex failure)")
			bytes = m.group(1).replace(" ", "")
			if len(bytes) % 2 != 0:
				raise TOPException("Invalid hexdump format (odd bytestring len)")
			for i in range(0, len(bytes), 2):
				byte = int(bytes[i:i+2], 16)
				bin.append(chr(byte))
		return "".join(bin)
	except (ValueError), e:
		raise TOPException("Invalid hexdump format (Integer error)")

def generateHexdump(mem):
	def toAscii(char):
		if char >= 32 and char <= 126:
			return chr(char)
		return "."

	ret = ""
	ascii = ""
	for i in range(0, len(mem)):
		if i % 16 == 0 and i != 0:
			ret += "  " + ascii + "\n"
			ascii = ""
		if i % 16 == 0:
			ret += "0x%04X:  " % i
		c = ord(mem[i])
		ret += "%02X" % c
		if (i % 2 != 0):
			ret += " "
		ascii += toAscii(c)
	ret += "  " + ascii + "\n\n"
	return ret

def dumpMem(mem):
	sys.stdout.write(generateHexdump(mem))
