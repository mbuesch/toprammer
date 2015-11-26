"""
#    TOP2049 Open Source programming suite
#
#    Lowlevel USB hardware access.
#
#    Copyright (c) 2012 Michael Buesch <m@bues.ch>
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

from util import *
from command_queue import *
try:
	import usb.core
	import usb.util
except (ImportError), e:
	print("Python USB (PyUSB) support module not found.\n"
	      "Please install python-usb.")
	sys.exit(1)


class FoundUSBDev(object):
	def __init__(self, usbdev):
		self.usbdev = usbdev

class HardwareAccessUSB(CommandQueue):
	"Lowlevel USB hardware access"

	TIMEOUT_MSEC = 2000

	@classmethod
	def scan(cls, checkCallback):
		"Scan for devices. Returns a list of FoundUSBDev()."
		devices = list(usb.core.find(find_all = True,
					     custom_match = checkCallback))
		devices = [ FoundUSBDev(dev) for dev in devices ]
		return devices

	def __init__(self, usbdev, maxPacketBytes, noQueue,
		     doRawDump=False):
		CommandQueue.__init__(self,
				      maxPacketBytes = maxPacketBytes,
				      synchronous = noQueue)
		self.doRawDump = doRawDump
		self.usbdev = usbdev

		self.__initUSB()

	def __initUSB(self):
		try:
			config = self.usbdev.configurations()[0]
			interface = config.interfaces()[0]

			# Find the endpoints
			self.bulkOut = None
			self.bulkIn = None
			for ep in interface.endpoints():
				if not self.bulkIn and \
				   usb.util.endpoint_type(ep.bmAttributes) == usb.util.ENDPOINT_TYPE_BULK and \
				   usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
					self.bulkIn = ep
				if not self.bulkOut and \
				   usb.util.endpoint_type(ep.bmAttributes) == usb.util.ENDPOINT_TYPE_BULK and \
				   usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
					self.bulkOut = ep
			if not self.bulkIn or not self.bulkOut:
				raise TOPException("Did not find all USB EPs")

			self.usbdev.set_configuration(config)
			self.bulkIn.clear_halt()
			self.bulkOut.clear_halt()

		except (usb.core.USBError), e:
			raise TOPException("USB error: " + str(e))

	def shutdown(self):
		"Shutdown the USB connection"
		try:
			usb.util.dispose_resources(self.usbdev)
		except (usb.core.USBError), e:
			raise TOPException("USB error: " + str(e))

	def send(self, data):
		try:
			assert(len(data) <= self.maxPacketBytes)
			if self.doRawDump:
				print("Sending command:")
				dumpMem(data)
			nrWritten = self.usbdev.write(
					self.bulkOut.bEndpointAddress,
					data,
					self.TIMEOUT_MSEC)
			if nrWritten != len(data):
				raise TOPException("USB bulk write error: "
					"short write")
		except (usb.core.USBError), e:
			raise TOPException("USB bulk write error: " + str(e))

	def receive(self, size):
		"""Receive 'size' bytes on the bulk-in ep."""
		# If there are blocked commands in the queue, send them now.
		self.flushCommands()
		try:
			ep = self.bulkIn.bEndpointAddress
			data = b"".join([ int2byte(b) for b in
					  self.usbdev.read(ep, size,
						self.TIMEOUT_MSEC) ])
			if len(data) != size:
				raise TOPException("USB bulk read error: Could not read the " +\
					"requested number of bytes (req %d, got %d)" % (size, len(data)))
			if self.doRawDump:
				print("Received data:")
				dumpMem(data)
		except (usb.core.USBError), e:
			raise TOPException("USB bulk read error: " + str(e))
		return data
