"""
#    TOP2049 Open Source programming suite
#
#    Generic command queue.
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

from .util import *
import time


class CommandQueue(object):
	"Generic hardware-command queue. Needs to be subclassed."

	def __init__(self, maxPacketBytes, synchronous=False):
		self.maxPacketBytes = maxPacketBytes
		self.synchronous = synchronous
		self.commandQueue = []

	def queueCommand(self, command):
		"""Queue a raw command for transmission."""
		if isinstance(command, str):
			# Compat for old code
			command = b"".join(int2byte(ord(c)) for c in command)
		assert isinstance(command, (bytes, bytearray))
		assert(len(command) <= self.maxPacketBytes)
		if self.synchronous:
			self.send(command)
		else:
			self.commandQueue.append(command)

	def runCommandSync(self, command):
		"""Run a command synchronously.
		This is slow. Don't use it without a very good reason."""
		self.flushCommands()
		self.queueCommand(command)
		self.flushCommands()

	def flushCommands(self, sleepSeconds=0):
		"""Flush the command queue."""
		command = b""
		for oneCommand in self.commandQueue:
			assert(len(oneCommand) <= self.maxPacketBytes)
			if len(command) + len(oneCommand) > self.maxPacketBytes:
				self.send(command)
				command = b""
			command += oneCommand
		if command:
			self.send(command)
		self.commandQueue = []
		if sleepSeconds:
			time.sleep(sleepSeconds)

	def send(self, data):
		raise NotImplementedError # Reimplement in subclass.

	def receive(self, size):
		raise NotImplementedError # Reimplement in subclass.
