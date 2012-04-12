"""
#    *.BIT file parser
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
try:
	import pkg_resources
except ImportError:
	print "Failed to import the 'pkg_resources' Python module."
	print "'pkg_resources' is part of the Python 'setuptools' package."
	print "On Debian Linux run:  apt-get install python-pkg-resources"
	sys.exit(1)

from util import *


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
		self.filename = ""
		self.srcfile = ""
		self.fpga = ""
		self.date = ""
		self.time = ""
		self.payload = ""

	def getFilename(self):
		return self.filename

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
			fd = open(filename, "rb")
			data = fd.read()
			fd.close()
		except (IOError), e:
			raise BitfileException("Failed to read \"" + filename + "\": " + e.strerror)
		self.filename = filename
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
		fieldId = byte2int(data[i + 0])
		if (fieldId == self.FIELD_SRCFILE):
			data = self.__parse16bitField(data, i + 1)
			self.srcfile = data.decode("ASCII").strip().strip("\x00")
			return len(data) + 3
		if (fieldId == self.FIELD_FPGA):
			data = self.__parse16bitField(data, i + 1)
			self.fpga = data.decode("ASCII").strip().strip("\x00")
			return len(data) + 3
		if (fieldId == self.FIELD_DATE):
			data = self.__parse16bitField(data, i + 1)
			self.date = data.decode("ASCII").strip().strip("\x00")
			return len(data) + 3
		if (fieldId == self.FIELD_TIME):
			data = self.__parse16bitField(data, i + 1)
			self.time = data.decode("ASCII").strip().strip("\x00")
			return len(data) + 3
		if (fieldId == self.FIELD_PAYLOAD):
			self.payload = self.__parse32bitField(data, i + 1)
			return len(self.payload) + 5
		raise BitfileException("Found unknown data field 0x%02X" % fieldId)

	def __parse16bitField(self, data, i):
		fieldLen = (byte2int(data[i + 0]) << 8) | byte2int(data[i + 1])
		return data[i + 2 : i + 2 + fieldLen]

	def __parse32bitField(self, data, i):
		fieldLen = (byte2int(data[i + 0]) << 24) | (byte2int(data[i + 1]) << 16) |\
			   (byte2int(data[i + 2]) << 8) | byte2int(data[i + 3])
		return data[i + 4 : i + 4 + fieldLen]

def __probeFile(fullpath):
	try:
		open(fullpath, "rb").close()
	except (IOError), e:
		return False
	return True

def bitfileFind(filename):
	"Search some standard paths for a bitfile"
	if not filename.endswith(".bit"):
		filename += ".bit"
	if filename.startswith("/"):
		if __probeFile(filename):
			return filename
	paths = ( ".", "./libtoprammer/fpga/bin", )
	for path in paths:
		fullpath = path + "/" + filename
		if __probeFile(fullpath):
			return fullpath
	fullpath = pkg_resources.resource_filename("libtoprammer",
						   "fpga/bin/" + filename)
	if __probeFile(fullpath):
		return fullpath
	return None

if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Usage: %s file.bit ACTION"
		print ""
		print "Actions:"
		print " GETSRC       - print the src-file field to stdout"
		print " GETFPGA      - print the fpga-type field to stdout"
		print " GETDATE      - print the date field to stdout"
		print " GETTIME      - print the time field to stdout"
		print " GETPAYLOAD   - print the payload field to stdout"
		sys.exit(1)
	filename = sys.argv[1]
	action = sys.argv[2].upper()

	b = Bitfile()
	b.parseFile(filename)
	if action == "GETSRC":
		sys.stdout.write(b.getSrcFile())
	if action == "GETFPGA":
		sys.stdout.write(b.getFPGA())
	if action == "GETDATE":
		sys.stdout.write(b.getDate())
	if action == "GETTIME":
		sys.stdout.write(b.getTime())
	if action == "GETPAYLOAD":
		sys.stdout.write(b.getPayload())
