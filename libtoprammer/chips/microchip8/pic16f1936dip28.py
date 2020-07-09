"""
#    TOP2049 Open Source programming suite
#
#   Microchip PIC16F1936 dip28
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

from .microchip8_splittedPMarea_hasResetPC import *

class Chip_Pic16F1936dip28(microchip8_splittedPMarea_hasResetPC):
		
	nLatches = 8
	hasEEPROM = True

	def __init__(self):
		microchip8_splittedPMarea_hasResetPC.__init__(self,
			chipPackage="dip28",
			chipPinVCC=20,
			chipPinsVPP=1,
			chipPinGND=19,
			signature=b"\x68\x23",
			flashPageSize=0x2000,
			flashPages=1,
			eepromPageSize=256,
			eepromPages=1,
			fuseBytes=4
			)

fuseDesc = (
	BitDescription(0, "FOSC[0], 000=LP, 001=XT, 010=HS, 011=EXTRC"),
	BitDescription(1, "FOSC[1], 100=INTOSC, 101=ECL - Low power mode"),
	BitDescription(2, "FOSC[2], 110=ECM - Medium power mode, 111=ECH - High power mode"),
	BitDescription(3, "WDTE[0], 00=WDT disabled, 11=WDT enabled"),
	BitDescription(4, "WDTE[1]"),
	BitDescription(5, "nPWRTE"),
	BitDescription(6, "MCLRE, 1=nMCLR/Vpp pin is nMCLR, weak pull-up enabled, ignored if LVP=1 "),
	BitDescription(7, "nCP 1=program memory code protection is disabled"),
	BitDescription(8, "nCPD, 1=data memory code protection is disabled"),
	BitDescription(9, "BOREN[0], 00=BOR disabled"),
	BitDescription(10, "BOREN[1]"),
	BitDescription(11, "nCLKOUTEN, 0=CLKOUT is enabled on CLKOUT pin"),
	BitDescription(12, "IESO, 0=Internal/External Switchover mode is disabled"),
	BitDescription(13, "FCMEM, 0=Fail-Safe Clock Monitor is disabled"),
	BitDescription(14, "NA"),
	BitDescription(15, "NA"),
	
	BitDescription(16, "WRT[0], 11=Write protection off"),
	BitDescription(17, "WRT[1]"),
	BitDescription(18, "Unused"),
	BitDescription(19, "Unused"),
	BitDescription(20, "VCAPEN[0] - only for PIC16F193x, 00=Vcap enabled on RA0"),
	BitDescription(21, "VCAPEN[1], 01=Vcap enabled on RA5, 10=Vcap enabled on RA6, 11=disabled "),
	BitDescription(22, "Unused"),
	BitDescription(23, "Unused"),
	BitDescription(24, "PLLEN, 0=4xPLL disabled"),
	BitDescription(25, "STVREN, 1=Stack overflow or underflow will cause a reset"),
	BitDescription(26, "BORV, 1=Brown-out Reset voltage set to 1.9V"),
	BitDescription(27, "Unused"),
	BitDescription(28, "nDEBUG, 0=ICSPCLK and ICSPDAT are dedicated to the debugger"),
	BitDescription(29, "LVP 1=Low-voltage programming enabled"),
	BitDescription(30, "NA"),
	BitDescription(31, "NA"),
)

ChipDescription(
	Chip_Pic16F1936dip28,
	bitfile="microchip01dip28",
	chipID="pic16f1936dip28",
	runtimeID=(0xDE07, 0x01),
	chipVendors="Microchip",
	description="PIC16F1936, PIC16LF1936",
	packages=(("dip28", ""),),
	fuseDesc=fuseDesc, 	
	maintainer="Pavel Stemberk <stemberk@gmail.com>",
)
