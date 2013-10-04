"""
#    TOP2049 Open Source programming suite
#
#    pic8_splittedPMarea - file for newer 8bit PIC MCUs
#
#    Copyright (c) 2013 Pavel Stemberk <stemberk@gmail.com>
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

from libtoprammer.chips.microchip8.microchip8_splittedPMarea import *

class microchip8_splittedPMarea_hasResetPC(microchip8_splittedPMarea):
	
    CMD_RESET_ADDRESS	 = 0x16
    
    userIDLocationSize = 4
    voltageVDD = 3
    voltageVPP = 8.5
    
    logicalFlashProgramMemorySize = 0x8000
    logicalFlashConfigurationMemorySize = 0x8000    
    
    def __init__(self,
	    chipPackage, chipPinVCC, chipPinsVPP, chipPinGND,
	    signature,
	    flashPageSize, flashPages,
	    eepromPageSize, eepromPages,
	    fuseBytes
	    ):
	microchip8_splittedPMarea.__init__(self, chipPackage, chipPinVCC, chipPinsVPP, chipPinGND, signature, flashPageSize, flashPages, eepromPageSize, eepromPages, fuseBytes)

    def setPC(self, address):
	if(self.isInsideProgramMemoryArea):
	    if(address >= self.logicalFlashProgramMemorySize):
		raise(TOPException('Cannot set PC to address inside PM {:x}'.format(address)))
	    if(address < self.PC):
		self.resetPC()
		self.setPC(address)
	else:
	    if(address < self.logicalFlashProgramMemorySize):
		raise(TOPException('Cannot set PC to address outside PM {:x}'.format(address)))
	    if(address < self.PC):
		self.resetPC()
		self.enterConfigArea()
		self.setPC(address)
	while(self.PC != address):
	    self.incrementPC(1)
		    
    def resetPC(self):
	if hasattr(self, 'osccalAddr'):
	    if not hasattr(self, 'CMD_RESET_ADDRESS'):
		print("reset instruction is not supported")
		self.exitPM()
		self.enterPM()
	else:
	    self.sendCommand(0, 0, 0, self.CMD_RESET_ADDRESS)
	self.PC = 0
	self.isInsideProgramMemoryArea = True
    
