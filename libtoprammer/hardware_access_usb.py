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
	import usb
except (ImportError), e:
	print "Python USB support module not found. Please install python-usb."
	sys.exit(1)


class FoundUSBDev(object):
	def __init__(self, usbdev, busNr, devNr):
		self.usbdev = usbdev
		self.busNr = busNr
		self.devNr = devNr

class HardwareAccessUSB(CommandQueue):
	"Lowlevel USB hardware access"

	TIMEOUT_MSEC = 2000

	@classmethod
	def scan(cls, checkCallback):
		"Scan for devices. Returns a list of FoundUSBDev()."
		devices = []
		for bus in usb.busses():
			for dev in bus.devices:
				if not checkCallback(dev):
					continue
				try:
					busNr = int(bus.dirname, 10)
					devNr = int(dev.filename, 10)
				except (ValueError), e:
					continue
				devices.append(FoundUSBDev(dev, busNr, devNr))
		return devices

	def __init__(self, usbdev, maxPacketBytes, noQueue,
		     doRawDump=False):
		CommandQueue.__init__(self,
				      maxPacketBytes = maxPacketBytes,
				      synchronous = noQueue)
		self.doRawDump = doRawDump
		self.usbdev = usbdev
		self.usbh = None

		self.__initUSB()

	def __initUSB(self):
		try:
			self.usbh = self.usbdev.open()
			config = self.usbdev.configurations[0]
			interface = config.interfaces[0][0]

			# Find the endpoints
			self.bulkOut = None
			self.bulkIn = None
			for ep in interface.endpoints:
				if not self.bulkIn and \
				   ep.type == usb.ENDPOINT_TYPE_BULK and \
				   (ep.address & (usb.ENDPOINT_IN | usb.ENDPOINT_OUT)) == usb.ENDPOINT_IN:
					self.bulkIn = ep
				if not self.bulkOut and \
				   ep.type == usb.ENDPOINT_TYPE_BULK and \
				   (ep.address & (usb.ENDPOINT_IN | usb.ENDPOINT_OUT)) == usb.ENDPOINT_OUT:
					self.bulkOut = ep
			if not self.bulkIn or not self.bulkOut:
				raise TOPException("Did not find all USB EPs")

			self.usbh.setConfiguration(config)
			self.usbh.claimInterface(interface)
			self.usbh.setAltInterface(interface)
			self.usbh.clearHalt(self.bulkOut.address)
			self.usbh.clearHalt(self.bulkIn.address)
		except (usb.USBError), e:
			self.usbh = None
			raise TOPException("USB error: " + str(e))

	def shutdown(self):
		"Shutdown the USB connection"
		try:
			if self.usbh:
				self.usbh.releaseInterface()
				self.usbh = None
		except (usb.USBError), e:
			raise TOPException("USB error: " + str(e))

	def send(self, data):
		try:
			assert(len(data) <= self.maxPacketBytes)
			if self.doRawDump:
				print("Sending command:")
				dumpMem(data)
			self.usbh.bulkWrite(self.bulkOut.address, data,
					    self.TIMEOUT_MSEC)
		except (usb.USBError), e:
			raise TOPException("USB bulk write error: " + str(e))

	def receive(self, size):
		"""Receive 'size' bytes on the bulk-in ep."""
		# If there are blocked commands in the queue, send them now.
		self.flushCommands()
		try:
			ep = self.bulkIn.address
			data = b"".join([ int2byte(b) for b in
					  self.usbh.bulkRead(ep, size,
						self.TIMEOUT_MSEC) ])
			if len(data) != size:
				raise TOPException("USB bulk read error: Could not read the " +\
					"requested number of bytes (req %d, got %d)" % (size, len(data)))
			if self.doRawDump:
				print("Received data:")
				dumpMem(data)
		except (usb.USBError), e:
			raise TOPException("USB bulk read error: " + str(e))
		return data
