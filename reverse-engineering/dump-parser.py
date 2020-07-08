#!/usr/bin/env python
"""
#    TOP2049 Open Source programming suite
#
#    USB dump parser
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
import re

packethdr_re = re.compile(r"Dev\s+([0-9a-fA-F]{4,4}):([0-9a-fA-F]{4,4})\s+EP([0-9a-fA-F]+)\s+(\w+)\s(\w+)\s+len=(\d+)")
payload_re = re.compile(r"\[([0-9a-fA-F]+)\]:\s+([0-9a-fA-F\s]+)\s+.+")


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
		c = mem[i]
		ret += "%02X" % c
		if (i % 2 != 0):
			ret += " "
		ascii += toAscii(c)
	ret += "  " + ascii + "\n\n"
	return ret

def dumpMem(mem):
	sys.stdout.write(generateHexdump(mem))

def dumpInstr(instr, description):
	for i in instr:
		sys.stdout.write("%02X" % i)
	sys.stdout.write("  " * (10 - len(instr)))
	sys.stdout.write(": " + description)
	sys.stdout.write("\n")

def parseBulkIn(data):
	if len(data) == 64:
		print("Read buffer register")
		dumpMem(data)

def parseBulkOut(data):
	i = 0
	while i < len(data):
		if data[i] == 0x00:
			dumpInstr(data[i:i+1], "Delay 4 usec")
		elif data[i] == 0x01:
			dumpInstr(data[i:i+1], "Read byte from FPGA")
		elif data[i] == 0x07:
			dumpInstr(data[i:i+1], "Read buffer register request")
		elif data[i] == 0x0A:
			dumpInstr(data[i:i+3], "Write 0x%02X to the FPGA at address 0x%02X" % (data[i+2], data[i+1]))
			i += 2
		elif data[i] == 0x0B:
			dumpInstr(data[i:i+2], "Read data from FPGA at address 0x%02X" % (data[i+1]))
			i += 1
		elif data[i] == 0x0E and data[i+1] == 0x11:
			dumpInstr(data[i:i+4], "Read device ID request")
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x12:
			centivolts = data[i+2]
			dumpInstr(data[i:i+4], "Set VPP to %.2f Volts" % (float(centivolts) / 10))
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x13:
			centivolts = data[i+2]
			dumpInstr(data[i:i+4], "Set VCC to %.2f Volts" % (float(centivolts) / 10))
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x14:
			dumpInstr(data[i:i+4], "Loading VPP layout %d" % data[i+1])
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x15:
			dumpInstr(data[i:i+4], "Loading VCC layout %d" % data[i+1])
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x16:
			dumpInstr(data[i:i+4], "Loading GND layout %d" % data[i+1])
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x20:
			dumpInstr(data[i:i+4], "Unknown 0x0E20%02X%02X" % (data[i+2], data[i+3]))
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x21:
			dumpInstr(data[i:i+4], "Initiate FPGA programming")
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x22:
			dumpInstr(data[i:i+4], "Upload FPGA configuration data")
			i += 63
		elif data[i] == 0x0E and data[i+1] == 0x25:
			dumpInstr(data[i:i+4], "Unknown 0x0E25")
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x28:
			op = "Disable"
			if data[i+2] == chr(0):
				op = "Enable"
			dumpInstr(data[i:i+4], "%s the ZIF socket" % op)
			i += 3
		elif data[i] == 0x0E and data[i+1] == 0x1F:
			dumpInstr(data[i:i+4], "Unknown 0x0E1F")
			i += 3
		elif data[i] == 0x0D:
			dumpInstr(data[i:i+1], "Unknown 0x0D")
		elif data[i] == 0x10:
			dumpInstr(data[i:i+2], "Write 0x%02X to the FPGA at address 0x10" % data[i+1])
			i += 1
		elif data[i] == 0x19:
			dumpInstr(data[i:i+1], "Unknown 0x19")
		elif data[i] == 0x1B:
			dumpInstr(data[i:i+1], "Delay 10 msec")
		elif data[i] == 0x34:
			dumpInstr(data[i:i+1], "Unknown 0x34")
		elif data[i] == 0x38:
			dumpInstr(data[i:i+2], "Unknown 0x38")
			i += 1
		elif data[i] == 0x39:
			dumpInstr(data[i:i+1], "Unknown 0x39")
		elif data[i] == 0x4A:
			dumpInstr(data[i:i+2], "Unknown 0x4A")
			i += 1
		elif data[i] == 0x4B:
			dumpInstr(data[i:i+2], "Unknown 0x4B")
			i += 1
		else:
			print("UNKNOWN INSTRUCTION 0x%02X. Aborting..." % data[i])
			for j in range(i, len(data)):
				sys.stdout.write("%02X " % data[j])
			print("")
			sys.exit(1)
		i += 1

def parseDumpFile(fd):
	transtype = None
	bulkData = []
	for line in fd.readlines():
		if transtype == "BULK":
			# Bulk IN or OUT transfer
			m = payload_re.match(line)
			if m:
				offset = int(m.group(1), 16)
				dataString = m.group(2)

				dataString = dataString.replace(" ", "").strip()
				assert(len(dataString) % 2 == 0)
				for i in range(0, len(dataString), 2):
					byteStr = dataString[i:i+2]
					bulkData.append(int(byteStr, 16))
			else:
				# Transfer done
				assert(len(bulkData) == length)
				if direction == "IN":
					parseBulkIn(bulkData)
				elif direction == "OUT":
					parseBulkOut(bulkData)
				else:
					assert(0)
				transtype = None
				bulkData = []

		m = packethdr_re.match(line)
		if m:
			vendor = int(m.group(1), 16)
			device = int(m.group(2), 16)
			ep = int(m.group(3), 16)
			transtype = m.group(4).upper()
			direction = m.group(5).upper()
			length = int(m.group(6))

def usage():
	print("dump-parser.py file.dump")

def main(argv):
	if len(argv) != 2:
		usage()
		return 1

	fd = open(argv[1])
	parseDumpFile(fd)

	return 0

if __name__ == "__main__":
	sys.exit(main(sys.argv))
