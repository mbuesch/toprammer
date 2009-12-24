"""
#    *.BIT file parser
#
#    Copyright (c) 2009 Michael Buesch <mb@bu3sch.de>
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

class BitfileException(Exception): pass

class Bitfile:
	# Magic header
	MAGIC		= "\x00\x09\x0f\xf0\x0f\xf0\x0f\xf0\x0f\xf0\x00\x00\x01"
	# Field IDs
	FIELD_SRCFILE	= 0x61
	FIELD_FPGA	= 0x62
	FIELD_DATE	= 0x63
	FIELD_TIME	= 0x64
	FIELD_PAYLOAD	= 0x65

	def __init__(self):
		self.srcfile = ""
		self.fpga = ""
		self.date = ""
		self.time = ""
		self.payload = ""

	def getSrcFile(self):
		return self.srcfile

	def getFPGA(self):
		return self.fpga

	def getDate(self):
		return self.date

	def getTime(self):
		return self.time

	def getPayload(self):
		return self.payload

	def parseFile(self, filename):
		try:
			data = file(filename, "rb").read()
		except (IOError), e:
			raise BitfileException("Failed to read \"" + filename + "\": " + e.strerror)
		self.__parse(data)

	def __parse(self, data):
		try:
			magic = data[0:len(self.MAGIC)]
			if magic != self.MAGIC:
				raise BitfileException("Invalid magic header")
			i = len(self.MAGIC)
			while i < len(data):
				i += self.__parseNextField(data, i)
		except (IndexError), e:
			raise BitfileException("Failed to parse BIT file")
		if not self.fpga:
			raise BitfileException("No FPGA ID string found")
		if not self.payload:
			raise BitfileException("No payload found")

	def __parseNextField(self, data, i):
		fieldId = ord(data[i + 0])
		if (fieldId == self.FIELD_SRCFILE):
			self.srcfile = self.__parse16bitField(data, i + 1).strip()
			return len(self.srcfile) + 3
		if (fieldId == self.FIELD_FPGA):
			self.fpga = self.__parse16bitField(data, i + 1).strip()
			return len(self.fpga) + 3
		if (fieldId == self.FIELD_DATE):
			self.date = self.__parse16bitField(data, i + 1).strip()
			return len(self.date) + 3
		if (fieldId == self.FIELD_TIME):
			self.time = self.__parse16bitField(data, i + 1).strip()
			return len(self.time) + 3
		if (fieldId == self.FIELD_PAYLOAD):
			self.payload = self.__parse32bitField(data, i + 1)
			return len(self.payload) + 5
		raise BitfileException("Found unknown data field 0x%02X" % fieldId)

	def __parse16bitField(self, data, i):
		fieldLen = (ord(data[i + 0]) << 8) | ord(data[i + 1])
		return data[i + 2 : i + 2 + fieldLen]

	def __parse32bitField(self, data, i):
		fieldLen = (ord(data[i + 0]) << 24) | (ord(data[i + 1]) << 16) |\
			   (ord(data[i + 2]) << 8) | ord(data[i + 3])
		return data[i + 4 : i + 4 + fieldLen]

if __name__ == "__main__":
	b = Bitfile()
	b.parseFile(sys.argv[1])
	print "Source file", b.getSrcFile()
	print "FPGA", b.getFPGA()
	print "Date", b.getDate()
	print "Time", b.getTime()
