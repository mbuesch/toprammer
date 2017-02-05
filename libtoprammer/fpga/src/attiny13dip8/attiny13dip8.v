/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel Tiny13 DIP8
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2010-2012 Michael Buesch <m@bues.ch>
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

`BOTTOMHALF_BEGIN(attiny13dip8, 1, 1)
	reg [7:0] prog_count;
	`define CMD_SENDINSTR	1

	reg dut_sdi;
	reg dut_sii;
	reg dut_sci_manual;
	reg dut_sci_auto;
	wire dut_sci;
	reg dut_sdo_driven;
	reg dut_sdo_value;
	reg dut_rst_driven;
	reg dut_rst_value;
	`define DUT_SDO		33
	reg [10:0] sdi_buf;
	reg [10:0] sii_buf;
	reg [10:0] sdo_buf;

	`INITIAL_BEGIN
		prog_count <= 0;
		dut_sdi <= 0;
		dut_sii <= 0;
		dut_sci_manual <= 0;
		dut_sci_auto <= 0;
		dut_sdo_driven <= 0;
		dut_sdo_value <= 0;
		dut_rst_driven <= 0;
		dut_rst_value <= 0;
		sdi_buf <= 0;
		sii_buf <= 0;
		sdo_buf <= 0;
	`INITIAL_END

	`ASYNCPROC_BEGIN
		if (`CMD_IS(`CMD_SENDINSTR)) begin
			case (`CMD_STATE)
			0: begin
				dut_sdi <= sdi_buf[10 - prog_count];
				dut_sii <= sii_buf[10 - prog_count];
				`CMD_STATE_SET(1)
				`UDELAY(1)
			end
			1: begin
				dut_sci_auto <= 1;	/* CLK hi */
				`CMD_STATE_SET(2)
				`UDELAY(1)
			end
			2: begin
				sdo_buf[10 - prog_count] <= zif[`DUT_SDO];
				prog_count <= prog_count + 1;
				`CMD_STATE_SET(3)
				`UDELAY(1)
			end
			3: begin
				dut_sci_auto <= 0;	/* CLK lo */
				`UDELAY(1)
				if (prog_count == 11) begin
					`CMD_FINISH
					prog_count <= 0;
				end else begin
					`CMD_STATE_SET(0)
				end
			end
			endcase
		end
	`ASYNCPROC_END

	`DATAWRITE_BEGIN
		`ADDR(2): begin /* Run command */
			`CMD_RUN(in_data)
		end
		`ADDR(3): begin /* Load SDI sequence */
			sdi_buf[1:0] <= 0;
			sdi_buf[9:2] <= in_data;
			sdi_buf[10] <= 0;
		end
		`ADDR(4): begin /* Load SII sequence */
			sii_buf[1:0] <= 0;
			sii_buf[9:2] <= in_data;
			sii_buf[10] <= 0;
		end
		`ADDR(5): begin /* Set signals manually */
			dut_sci_manual <= in_data[0];	/* SCI */
			dut_sdo_driven <= in_data[1];	/* SDO drive-enable */
			dut_sdo_value <= in_data[2];	/* SDO drive-value */
			dut_rst_driven <= in_data[3];	/* RESET drive-enable */
			dut_rst_value <= in_data[4];	/* RESET drive-value */
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin /* Get SDO sequence high (bits 3-10) */
			out_data[7:0] <= sdo_buf[10:3];
		end
		`ADDR(2): begin /* Read status */
			out_data[0] <= `CMD_IS_RUNNING;	/* busy */
			out_data[1] <= zif[`DUT_SDO];	/* Raw SDO pin access */
		end
		`ADDR(3): begin /* Get SDO sequence low (bits 0-7) */
			out_data[7:0] <= sdo_buf[7:0];
		end
	`DATAREAD_END

	assign dut_sci = `CMD_IS_RUNNING ? dut_sci_auto : dut_sci_manual;

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)	`ZIF_UNUSED(5)	`ZIF_UNUSED(6)
	`ZIF_UNUSED(7)	`ZIF_UNUSED(8)	`ZIF_UNUSED(9)
	`ZIF_UNUSED(10)	`ZIF_UNUSED(11)	`ZIF_UNUSED(12)
	`ZIF_UNUSED(13)	`ZIF_UNUSED(14)
	bufif0(zif[15], dut_rst_value, !dut_rst_driven);	/* RESET */
	bufif0(zif[16], dut_sci, low);				/* SCI */
	bufif0(zif[17], low, high);				/* PB4 */
	bufif0(zif[18], low, low);				/* GND */
	`ZIF_UNUSED(19)	`ZIF_UNUSED(20)	`ZIF_UNUSED(21)
	`ZIF_UNUSED(22)	`ZIF_UNUSED(23)	`ZIF_UNUSED(24)
	`ZIF_UNUSED(25)	`ZIF_UNUSED(26)	`ZIF_UNUSED(27)
	`ZIF_UNUSED(28)	`ZIF_UNUSED(29)	`ZIF_UNUSED(30)
	bufif0(zif[31], dut_sdi, low);				/* SDI */
	bufif0(zif[32], dut_sii, low);				/* SII */
	bufif0(zif[33], dut_sdo_value, !dut_sdo_driven);	/* SDO */
	bufif0(zif[34], high, low);				/* VCC */
	`ZIF_UNUSED(35)	`ZIF_UNUSED(36)	`ZIF_UNUSED(37)
	`ZIF_UNUSED(38)	`ZIF_UNUSED(39)	`ZIF_UNUSED(40)
	`ZIF_UNUSED(41)	`ZIF_UNUSED(42)	`ZIF_UNUSED(43)
	`ZIF_UNUSED(44)	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)
	`ZIF_UNUSED(47)	`ZIF_UNUSED(48)
`BOTTOMHALF_END
