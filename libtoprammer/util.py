"""
#    TOP2049 Open Source programming suite
#
#    Utility functions
#
#    Copyright (c) 2009-2011 Michael Buesch <m@bues.ch>
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
import math
import random


class TOPException(Exception): pass


def byte2int(byte):
	if isinstance(byte, int): # It's already int
		assert 0 <= byte <= 0xFF
		return byte
	if isinstance(byte, str): # Compat for old code
		assert len(byte) == 1
		return ord(byte)
	assert isinstance(byte, (bytes, bytearray))
	assert len(byte) == 1
	return byte[0]

def int2byte(integer):
	if isinstance(integer, (bytes, bytearray)): # It's already bytes
		return bytes(integer)
	assert isinstance(integer, int)
	assert 0 <= integer <= 0xFF
	return b"%c" % integer

def hex2bin(hexdata):
	assert(len(hexdata) % 2 == 0)
	return b"".join(int2byte(int(hexdata[i:i+2], 16))
			for i in range(len(hexdata), 2))

def byte2hex(byte):
	return "%02X" % byte2int(byte)

def bytes2hex(bindata):
	if not bindata:
		return ""
	return "".join(byte2hex(b) for b in bindata)

def byte2ascii(c):
	c = byte2int(c)
	if c >= 32 and c <= 126:
		return "%c" % c
	return "."

def bytes2ascii(bindata):
	if not bindata:
		return ""
	return "".join(byte2ascii(b) for b in bindata)

def str2bool(string):
	string = str(string).lower().strip()
	if string in ("false", "off", "no"):
		return False
	if string in ("true", "on", "yes"):
		return True
	try:
		return bool(int(string, 10))
	except (ValueError) as e:
		pass
	return None

def genRandomBlob(size):
	return b"".join(int2byte(random.randint(0, 0xFF))
			for x in range(size))

def bit(bitNr):
	return 1 << bitNr

def nrBitsSet(integer):
	count = 0
	while integer:
		count += (integer & 1)
		integer >>= 1
	return count

def roundup(x, y):
	x, y = int(x), int(y)
	return ((x + (y - 1)) // y) * y

hexdump_re = re.compile(r"0x[0-9a-fA-F]+:\s+([0-9a-fA-F\s]+)\s*.*")

def parseHexdump(dump):
	try:
		if isinstance(dump, (bytes, bytearray)):
			dump = dump.decode("ASCII")
		binData = []
		for line in dump.splitlines():
			line = line.strip()
			if not line:
				continue
			m = hexdump_re.match(line)
			if not m:
				raise TOPException("Invalid hexdump format (regex failure)")
			data = m.group(1)
			idx = data.find("  ")
			if idx >= 0:
				data = data[:idx] # Strip ascii section
			data = data.replace(" ", "")
			if len(data) % 2 != 0:
				raise TOPException("Invalid hexdump format (odd bytestring len)")
			for i in range(0, len(data), 2):
				byte = int(data[i:i+2], 16)
				binData.append(int2byte(byte))
		return b"".join(binData)
	except (ValueError, UnicodeError) as e:
		raise TOPException("Invalid hexdump format (Integer error)")

def generateHexdump(mem):
	ret = ""
	asc = ""
	for i in range(0, len(mem)):
		if i % 16 == 0 and i != 0:
			ret += "  " + asc + "\n"
			asc = ""
		if i % 16 == 0:
			ret += "0x%04X:  " % i
		c = byte2int(mem[i])
		ret += "%02X" % c
		if (i % 2 != 0):
			ret += " "
		asc += byte2ascii(mem[i])
	ret += "  " + asc + "\n\n"
	return ret

def dumpMem(mem):
	sys.stdout.write(generateHexdump(mem))

class IO_ihex(object):
	TYPE_DATA = 0
	TYPE_EOF  = 1
	TYPE_ESAR = 2
	TYPE_SSAR = 3
	TYPE_ELAR = 4
	TYPE_SLAR = 5

	def autodetect(self, data):
		try:
			self.toBinary(data)
		except (TOPException) as e:
			return False
		return True

	def toBinary(self, ihexData, addressRange=None, defaultBytes=b"\xFF"):
		binData = []
		checksumWarned = False
		doublewriteWarned = False
		addrBias = addressRange.startAddress if addressRange else 0
		try:
			if isinstance(ihexData, (bytes, bytearray)):
				ihexData = ihexData.decode("ASCII")
			lines = ihexData.splitlines()
			hiAddr = 0
			segment = 0
			for line in lines:
				line = line.strip()
				if len(line) == 0:
					continue
				if len(line) < 11 or (len(line) - 1) % 2 != 0:
					raise TOPException("Invalid IHEX format (length error)")
				if line[0] != ':':
					raise TOPException("Invalid IHEX format (magic error)")
				count = int(line[1:3], 16)
				if len(line) != count * 2 + 11:
					raise TOPException("Invalid IHEX format (count error)")
				addr = (int(line[3:5], 16) << 8) | int(line[5:7], 16)
				addr |= hiAddr << 16
				addr += segment * 16
				if hiAddr and segment:
					print("WARNING: IHEX has ESAR and ELAR record")
				type = int(line[7:9], 16)
				checksum = 0
				for i in range(1, len(line), 2):
					byte = int(line[i:i+2], 16)
					checksum = (checksum + byte) & 0xFF
				checksum = checksum & 0xFF
				if checksum != 0 and not checksumWarned:
					checksumWarned = True
					print("WARNING: Invalid IHEX format (checksum error)")

				if type == self.TYPE_EOF:
					break
				if type == self.TYPE_ESAR:
					if count != 2:
						raise TOPException("Invalid IHEX format (inval ESAR)")
					segment = (int(line[9:11], 16) << 8) | int(line[11:13], 16)
					continue
				if type == self.TYPE_ELAR:
					if count != 2:
						raise TOPException("Invalid IHEX format (inval ELAR)")
					hiAddr = (int(line[9:11], 16) << 8) | int(line[11:13], 16)
					continue
				if addressRange and addr < addressRange.startAddress:
					continue
				if addressRange and addr > addressRange.endAddress:
					continue
				if type == self.TYPE_DATA:
					if len(binData) < addr - addrBias + count: # Reallocate
						bytesToAdd = addr - addrBias + count - len(binData)
						for i in range(bytesToAdd):
							defOffs = len(binData) % len(defaultBytes)
							binData += [ defaultBytes[defOffs], ]
					for i in range(9, 9 + count * 2, 2):
						byte = int2byte(int(line[i:i+2], 16))
						offset = (i - 9) // 2 + addr - addrBias
						if binData[offset] != defaultBytes[offset % len(defaultBytes)] and \
						   not doublewriteWarned:
							doublewriteWarned = True
							print("Invalid IHEX format (Wrote twice to same location)")
						binData[offset] = byte
					continue
				raise TOPException("Invalid IHEX format (unsup type %d)" % type)
		except (ValueError, UnicodeError) as e:
			raise TOPException("Invalid IHEX format (digit format)")
		return b"".join(binData)

	def fromBinary(self, binData):
		ihex = []
		addr = 0
		for i in range(0, len(binData), 16):
			if addr > 0xFFFF:
				checksum = 0
				ihex.append(":%02X%04X%02X" % (2, 0, self.TYPE_ELAR))
				checksum += 2 + 0 + 0 + self.TYPE_ELAR
				a = (addr >> 16) & 0xFFFF
				ihex.append("%04X" % a)
				checksum += ((a >> 8) & 0xFF) + (a & 0xFF)
				checksum = ((checksum ^ 0xFF) + 1) & 0xFF
				ihex.append("%02X\n" % checksum)
				addr -= 0xFFFF
			checksum = 0
			size = min(len(binData) - i, 16)
			ihex.append(":%02X%04X%02X" % (size, addr, self.TYPE_DATA))
			checksum += size + ((addr >> 8) & 0xFF) + (addr & 0xFF) + self.TYPE_DATA
			for j in range(0, size):
				data = byte2int(binData[i + j])
				checksum = (checksum + data) & 0xFF
				ihex.append("%02X" % data)
			checksum = ((checksum ^ 0xFF) + 1) & 0xFF
			ihex.append("%02X\n" % checksum)
			addr += size
		ihex.append(":00000001FF\n")
		return "".join(ihex)

class IO_ahex(object):
	def autodetect(self, data):
		try:
			self.toBinary(data)
		except (TOPException) as e:
			return False
		return True

	def toBinary(self, data, addressRange=None, defaultBytes=b"\xFF"):
		# defaultBytes is ignored
		binData = parseHexdump(data)
		if addressRange:
			binData = binData[addressRange.startAddress : addressRange.endAddress + 1]
		return binData

	def fromBinary(self, data):
		return generateHexdump(data)

class IO_binary(object):
	def autodetect(self, data):
		return True

	def toBinary(self, data, addressRange=None, defaultBytes=b"\xFF"):
		# defaultBytes is ignored
		if addressRange:
			data = data[addressRange.startAddress : addressRange.endAddress + 1]
		return data

	def fromBinary(self, data):
		return data

def IO_autodetect(data):
	"Returns an IO_... object for the data."
	if IO_ihex().autodetect(data):
		return IO_ihex
	elif IO_ahex().autodetect(data):
		return IO_ahex
	elif IO_binary().autodetect(data):
		return IO_binary
	assert(0) # Can't reach, because binary will always match.
