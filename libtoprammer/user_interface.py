"""
#    TOP2049 Open Source programming suite
#
#    Generic user interface support
#
#    Copyright (c) 2009-2010 Michael Buesch <m@bues.ch>
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


class AbstractUserInterface:
	"Abstract user interface class. Subclass it."

	# Progress meter IDs
	PROGRESSMETER_CHIPACCESS	= 0 # Programming/reading progress meter
	PROGRESSMETER_USER		= 100 # IDs equal or bigger than this are available to the app

	def progressMeterInit(self, meterId, message, nrSteps):
		pass # Do nothing by default

	def progressMeterFinish(self, meterId):
		pass # Do nothing by default

	def progressMeter(self, meterId, step):
		pass # Do nothing by default

	def warningMessage(self, message):
		pass # Do nothing by default

	def infoMessage(self, message):
		pass # Do nothing by default

	def debugMessage(self, message):
		pass # Do nothing by default

class ConsoleUserInterface(AbstractUserInterface):
	"Console based user interface."

	def progressMeterInit(self, meterId, message, nrSteps):
		if meterId != self.PROGRESSMETER_CHIPACCESS:
			return
		self.progressNrSteps = nrSteps
		self.progress = list(range(0, 100))
		self.__genericConsoleMessage(message + " [0%", newline=False)

	def progressMeterFinish(self, meterId):
		if meterId != self.PROGRESSMETER_CHIPACCESS:
			return
		if not self.progressNrSteps:
			self.progressMeter(meterId, 0)
		self.__genericConsoleMessage("100%]")

	def progressMeter(self, meterId, step):
		if meterId != self.PROGRESSMETER_CHIPACCESS:
			return
		if self.progressNrSteps:
			percent = (step * 100 // self.progressNrSteps)
		else:
			percent = 100
		for progress in list(self.progress):
			if progress > percent:
				break
			if progress == 25:
				self.__genericConsoleMessage("25%", newline=False)
			elif progress == 50:
				self.__genericConsoleMessage("50%", newline=False)
			elif progress == 75:
				self.__genericConsoleMessage("75%", newline=False)
			elif progress % 2 == 0:
				self.__genericConsoleMessage(".", newline=False)
			self.progress.remove(progress)

	def __genericConsoleMessage(self, message, newline=True):
		if newline:
			print(message)
		else:
			sys.stdout.write(message)
			sys.stdout.flush()

	def warningMessage(self, message):
		self.__genericConsoleMessage(message)

	def infoMessage(self, message):
		self.__genericConsoleMessage(message)

	def debugMessage(self, message):
		self.__genericConsoleMessage(message)
