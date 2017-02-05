/*
 *   TOP2049 Open Source programming suite
 *
 *   HM62256 SRAM
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2011-2012 Michael Buesch <m@bues.ch>
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

`include "common.vh"

`BOTTOMHALF_BEGIN(hm62256dip28, 10, 1)
	reg [14:0] dut_addr;
	reg [7:0] dut_data;
	reg dut_ce;
	reg dut_oe;
	reg dut_we;

	`INITIAL_NONE

	`ASYNCPROC_NONE

	`DATAWRITE_BEGIN
		`ADDR(0): begin /* Bulk write */
			dut_data <= in_data;
		end
		`ADDR(1): begin /* /CE, /OE, /WE */
			dut_ce <= in_data[0];
			dut_oe <= in_data[1];
			dut_we <= in_data[2];
		end
		`ADDR(2): begin /* Addr byte 0 */
			dut_addr[7:0] <= in_data[7:0];
		end
		`ADDR(3): begin /* Addr byte 1 */
			dut_addr[14:8] <= in_data[6:0];
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin /* Bulk read */
			out_data[0] <= zif[21];
			out_data[1] <= zif[22];
			out_data[2] <= zif[23];
			out_data[3] <= zif[25];
			out_data[4] <= zif[26];
			out_data[5] <= zif[27];
			out_data[6] <= zif[28];
			out_data[7] <= zif[29];
		end
	`DATAREAD_END

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)	`ZIF_UNUSED(5)	`ZIF_UNUSED(6)
	`ZIF_UNUSED(7)	`ZIF_UNUSED(8)	`ZIF_UNUSED(9)
	`ZIF_UNUSED(10)
	bufif0(zif[11], dut_addr[14], low);	/* A14 */
	bufif0(zif[12], dut_addr[12], low);	/* A12 */
	bufif0(zif[13], dut_addr[7], low);	/* A7 */
	bufif0(zif[14], dut_addr[6], low);	/* A6 */
	bufif0(zif[15], dut_addr[5], low);	/* A5 */
	bufif0(zif[16], dut_addr[4], low);	/* A4 */
	bufif0(zif[17], dut_addr[3], low);	/* A3 */
	bufif0(zif[18], dut_addr[2], low);	/* A2 */
	bufif0(zif[19], dut_addr[1], low);	/* A1 */
	bufif0(zif[20], dut_addr[0], low);	/* A0 */
	bufif0(zif[21], dut_data[0], !dut_oe);	/* DQ0 */
	bufif0(zif[22], dut_data[1], !dut_oe);	/* DQ1 */
	bufif0(zif[23], dut_data[2], !dut_oe);	/* DQ2 */
	bufif0(zif[24], low, low);		/* GND */
	bufif0(zif[25], dut_data[3], !dut_oe);	/* DQ3 */
	bufif0(zif[26], dut_data[4], !dut_oe);	/* DQ4 */
	bufif0(zif[27], dut_data[5], !dut_oe);	/* DQ5 */
	bufif0(zif[28], dut_data[6], !dut_oe);	/* DQ6 */
	bufif0(zif[29], dut_data[7], !dut_oe);	/* DQ7 */
	bufif0(zif[30], dut_ce, low);		/* /CE */
	bufif0(zif[31], dut_addr[10], low);	/* A10 */
	bufif0(zif[32], dut_oe, low);		/* /OE */
	bufif0(zif[33], dut_addr[11], low);	/* A11 */
	bufif0(zif[34], dut_addr[9], low);	/* A9 */
	bufif0(zif[35], dut_addr[8], low);	/* A8 */
	bufif0(zif[36], dut_addr[13], low);	/* A13 */
	bufif0(zif[37], dut_we, low);		/* /WE */
	bufif0(zif[38], high, low);		/* VCC */
	`ZIF_UNUSED(39)	`ZIF_UNUSED(40)	`ZIF_UNUSED(41)
	`ZIF_UNUSED(42)	`ZIF_UNUSED(43)	`ZIF_UNUSED(44)
	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)	`ZIF_UNUSED(47)
	`ZIF_UNUSED(48)
`BOTTOMHALF_END
