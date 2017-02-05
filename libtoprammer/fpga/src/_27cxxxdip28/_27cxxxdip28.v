/*
 *   TOP2049 Open Source programming suite
 *
 *   27c16dip28  UV/OTP EPROM
 *   27c32dip28  UV/OTP EPROM
 *   27c64dip28  UV/OTP EPROM
 *   27c128dip28 UV/OTP EPROM
 *   27c256dip28 UV/OTP EPROM
 *   27c512dip28 UV/OTP EPROM
 *   Various manufacturers
 *
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2012 Michael Buesch <m@bues.ch>
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

`BOTTOMHALF_BEGIN(_27cxxxdip28, 12, 1)
	reg [7:0] cdata;
	reg cdata_en;
	reg [15:0] caddr;
	reg ce;			/* !CE */
	reg prog_pulse_reg;	/* Programming pulse */
	reg [9:0] prog_pulse_length;
	reg [9:0] prog_pulse_count;
	reg prog_en;
	reg oe;			/* !OE */

	reg [2:0] ctype;	/* Chip type */
	`define CTYPE_16		0
	`define CTYPE_32		1
	`define CTYPE_64		2
	`define CTYPE_128		3
	`define CTYPE_256		4
	`define CTYPE_512		5

	`define CMD_PPULSE		0

	`INITIAL_BEGIN
		cdata <= 0;
		cdata_en <= 0;
		caddr <= 0;
		ce <= 1;
		prog_pulse_reg <= 1;
		prog_pulse_length <= 0;
		prog_pulse_count <= 0;
		prog_en <= 0;
		oe <= 1;
		ctype <= 0;
	`INITIAL_END

	wire prog_pulse;
	assign prog_pulse = prog_en ? prog_pulse_reg : high;

	`ASYNCPROC_BEGIN
		if (`CMD_IS(`CMD_PPULSE)) begin
			case (`CMD_STATE)
			0: begin
				prog_pulse_count <= prog_pulse_length;
				`CMD_STATE_SET(1)
			end
			1: begin
				prog_pulse_reg <= 0;
				prog_pulse_count <= prog_pulse_count - 1;
				`CMD_STATE_SET(2)
				`UDELAY(100)
			end
			2: begin
				if (prog_pulse_count == 0) begin
					prog_pulse_reg <= 1;
					`CMD_FINISH
				end else begin
					`CMD_STATE_SET(1)
				end
			end
			endcase
		end
	`ASYNCPROC_END

	`DATAWRITE_BEGIN
		`ADDR(0): begin /* Address low write */
			caddr[7:0] <= in_data[7:0];
		end
		`ADDR(1): begin /* Address high write */
			caddr[15:8] <= in_data[7:0];
		end
		`ADDR(2): begin /* Data pins write */
			cdata[7:0] <= in_data[7:0];
		end
		`ADDR(3): begin /* Flags write */
			cdata_en <= in_data[0];
			prog_en <= in_data[1];
			ce <= in_data[2];
			oe <= in_data[3];
		end
		`ADDR(4): begin /* Perform prog pulse */
			/* in_data[6:0] -> ppulse length, in 100us units.
			 * in_data[7] -> Length multiplier "times 8".
			 */
			if (in_data[7]) begin
				prog_pulse_length[2:0] <= 0;
				prog_pulse_length[9:3] <= in_data[6:0];
			end else begin
				prog_pulse_length[6:0] <= in_data[6:0];
				prog_pulse_length[9:7] <= 0;
			end
			`CMD_RUN(`CMD_PPULSE)
		end
		`ADDR(5): begin /* Set the chip type number */
			ctype[2:0] <= in_data[2:0];
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin /* Data pins read */
			out_data[2:0] <= zif[23:21];
			out_data[7:3] <= zif[29:25];
		end
		`ADDR(1): begin /* Flags read */
			out_data[0] <= `CMD_IS_RUNNING;
			out_data[7:1] <= 0;
		end
	`DATAREAD_END

	wire a11, a11_en;
	assign a11_en = (ctype >= `CTYPE_32) ? low : high;
	assign a11    = (ctype >= `CTYPE_32) ? caddr[11] : low;

	wire a12, a12_en;
	assign a12_en = (ctype >= `CTYPE_64) ? low : high;
	assign a12    = (ctype >= `CTYPE_64) ? caddr[12] : low;

	wire a13, a13_en;
	assign a13_en = (ctype >= `CTYPE_128) ? low : high;
	assign a13    = (ctype >= `CTYPE_128) ? caddr[13] : high;

	wire a14, a14_en;
	assign a14_en = (ctype >= `CTYPE_64) ? low : high;
	assign a14    = (ctype == `CTYPE_64 || ctype == `CTYPE_128) ?
			prog_pulse : caddr[14];

	wire a15, a15_en;
	assign a15_en = (ctype >= `CTYPE_512) ? low : high;
	assign a15    = (ctype >= `CTYPE_512) ? caddr[15] : low;

	wire oe_en;
	assign oe_en = (prog_en && (ctype == `CTYPE_32 || ctype == `CTYPE_512)) ?
			high : low;

	/* !CE and !P handling */
	wire pin20;
	assign pin20 = (prog_en &&
			ctype != `CTYPE_64 && ctype != `CTYPE_128) ?
			prog_pulse : ce;

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)	`ZIF_UNUSED(5)	`ZIF_UNUSED(6)
	`ZIF_UNUSED(7)	`ZIF_UNUSED(8)	`ZIF_UNUSED(9)
	`ZIF_UNUSED(10)
	bufif0(zif[11], a15, a15_en);			/* VPP (A15 on >= 512) */
	bufif0(zif[12], a12, a12_en);			/* A12 (>= 64) */
	bufif0(zif[13], caddr[7], low);			/* A7 */
	bufif0(zif[14], caddr[6], low);			/* A6 */
	bufif0(zif[15], caddr[5], low);			/* A5 */
	bufif0(zif[16], caddr[4], low);			/* A4 */
	bufif0(zif[17], caddr[3], low);			/* A3 */
	bufif0(zif[18], caddr[2], low);			/* A2 */
	bufif0(zif[19], caddr[1], low);			/* A1 */
	bufif0(zif[20], caddr[0], low);			/* A0 */
	bufif0(zif[21], cdata[0], !cdata_en);		/* O0 */
	bufif0(zif[22], cdata[1], !cdata_en);		/* O1 */
	bufif0(zif[23], cdata[2], !cdata_en);		/* O2 */
	bufif0(zif[24], low, low);			/* GND */
	bufif0(zif[25], cdata[3], !cdata_en);		/* O3 */
	bufif0(zif[26], cdata[4], !cdata_en);		/* O4 */
	bufif0(zif[27], cdata[5], !cdata_en);		/* O5 */
	bufif0(zif[28], cdata[6], !cdata_en);		/* O6 */
	bufif0(zif[29], cdata[7], !cdata_en);		/* O7 */
	bufif0(zif[30], pin20, low);			/* !CE or !P */
	bufif0(zif[31], caddr[10], low);		/* A10 */
	bufif0(zif[32], oe, oe_en);			/* !OE */
	bufif0(zif[33], a11, a11_en);			/* A11 (>= 32) */
	bufif0(zif[34], caddr[9], low);			/* A9 */
	bufif0(zif[35], caddr[8], low);			/* A8 */
	bufif0(zif[36], a13, a13_en);			/* A13 (>= 128) */
	bufif0(zif[37], a14, a14_en);			/* !P (A14 on >=256) */
	bufif0(zif[38], high, high);			/* VCC (>= 64) */
	`ZIF_UNUSED(39)	`ZIF_UNUSED(40)	`ZIF_UNUSED(41)
	`ZIF_UNUSED(42)	`ZIF_UNUSED(43)	`ZIF_UNUSED(44)
	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)	`ZIF_UNUSED(47)
	`ZIF_UNUSED(48)
`BOTTOMHALF_END
