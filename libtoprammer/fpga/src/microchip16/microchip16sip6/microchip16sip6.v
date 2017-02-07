/*
 *   TOP2049 Open Source programming suite
 *
 *   Microchip ICD2 SIP6 connection (implemented as DIP10)
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2014 Pavel Stemberk <stemberk@gmail.com>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License along
 *   with this program; if not, write to the Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

`include "microchip16.vh"

`ALL_WITHOUT_ZIF(microchip16sip6, 32'hDF05, 1)

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)	`ZIF_UNUSED(5)	`ZIF_UNUSED(6)
	`ZIF_UNUSED(7)	`ZIF_UNUSED(8)	`ZIF_UNUSED(9)
	`ZIF_UNUSED(10)	`ZIF_UNUSED(11)	`ZIF_UNUSED(12)
	`ZIF_UNUSED(13)	`ZIF_UNUSED(14) `ZIF_UNUSED(15)
	`ZIF_UNUSED(16)	`ZIF_UNUSED(17) `ZIF_UNUSED(18)
	`ZIF_UNUSED(19)	
	`ZIF_UNUSED(20)
	`ZIF_UNUSED(21)
	`ZIF_UNUSED(22)
	`ZIF_UNUSED(23)	`ZIF_UNUSED(24) `ZIF_UNUSED(25)
	bufif0(zif[26], dut_sci, low);                          /* SCI */
	bufif0(zif[27], dut_sdio_value, !dut_sdio_driven);      /* SDO */
	bufif0(zif[28], low, low);             /* GND */
	bufif0(zif[29], high, low);                /* VCC */
	bufif0(zif[30], low, dut_vpp);      /* VPP/Reset */	
	`ZIF_UNUSED(31)	`ZIF_UNUSED(32)	`ZIF_UNUSED(33)
	`ZIF_UNUSED(34)
	`ZIF_UNUSED(35)	`ZIF_UNUSED(36)	`ZIF_UNUSED(37)
	`ZIF_UNUSED(38)	`ZIF_UNUSED(39)	`ZIF_UNUSED(40)
	`ZIF_UNUSED(41)	`ZIF_UNUSED(42)	`ZIF_UNUSED(43)
	`ZIF_UNUSED(44)	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)
	`ZIF_UNUSED(47)	`ZIF_UNUSED(48)
`BOTTOMHALF_END
