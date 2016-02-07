/*
 *   TOP2049 Open Source programming suite
 *
 *   27c1024dip40  UV/OTP EPROM
 *   Various manufacturers
 *
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2012 Michael Buesch <m@bues.ch>
 *   Copyright (c) 2016 Tom van Leeuwen <gpl@tomvanleeuwen.nl>
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

`BOTTOMHALF_BEGIN(_27cxxxdip40, 13, 1)
	reg [15:0] cdata;
	reg cdata_en;
	reg [15:0] caddr;
	reg ce;			/* !CE */
	reg prog_pulse_reg;	/* Programming pulse */
	reg [9:0] prog_pulse_length;
	reg [9:0] prog_pulse_count;
	reg prog_en;
	reg oe;			/* !OE */

	reg [2:0] ctype;	/* Chip type */
	`define CTYPE_1024		0

	`define CMD_PPULSE		0

	initial begin
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
	end

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
		`ADDR(3): begin /* Data pins write */
			cdata[15:8] <= in_data[7:0];
		end
		`ADDR(4): begin /* Flags write */
			cdata_en <= in_data[0];
			prog_en <= in_data[1];
			ce <= in_data[2];
			oe <= in_data[3];
		end
		`ADDR(5): begin /* Perform prog pulse */
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
		`ADDR(6): begin /* Set the chip type number */
			ctype[2:0] <= in_data[2:0];
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin /* Data pins read, low byte */
			out_data[0] <= zif[23]; /* Note: pinning is in reversed order. */
			out_data[1] <= zif[22];
			out_data[2] <= zif[21];
			out_data[3] <= zif[20];
			out_data[4] <= zif[19];
			out_data[5] <= zif[18];
			out_data[6] <= zif[17];
			out_data[7] <= zif[16];
		end
		`ADDR(1): begin /* Data pins read, high byte */
			out_data[0] <= zif[14]; /* Note: pinning is in reversed order */
			out_data[1] <= zif[13];
			out_data[2] <= zif[12];
			out_data[3] <= zif[11];
			out_data[4] <= zif[10];
			out_data[5] <= zif[9];
			out_data[6] <= zif[8];
			out_data[7] <= zif[7];
		end
		`ADDR(2): begin /* Flags read */
			out_data[0] <= `CMD_IS_RUNNING;
			out_data[7:1] <= 0;
		end
	`DATAREAD_END
	
	
	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)
	// Top of chip, add 4 to DIL40 pin numbers to get ZIF pin number
	bufif0(zif[5], low, high);			/* VPP */
	bufif0(zif[6], ce, low);			/* CE */
	bufif0(zif[7], cdata[15], !cdata_en);		/* O15 */
	bufif0(zif[8], cdata[14], !cdata_en);		/* O14 */
	bufif0(zif[9], cdata[13], !cdata_en);		/* O13 */
	bufif0(zif[10], cdata[12], !cdata_en);		/* O12 */
	bufif0(zif[11], cdata[11], !cdata_en);		/* O11 */
	bufif0(zif[12], cdata[10], !cdata_en);		/* O10 */
	bufif0(zif[13], cdata[9], !cdata_en);		/* O9 */
	bufif0(zif[14], cdata[8], !cdata_en);		/* O8 */
	bufif0(zif[15], low, low);			/* GND */
	bufif0(zif[16], cdata[7], !cdata_en);		/* O8 */
	bufif0(zif[17], cdata[6], !cdata_en);		/* O8 */
	bufif0(zif[18], cdata[5], !cdata_en);		/* O8 */
	bufif0(zif[19], cdata[4], !cdata_en);		/* O8 */
	bufif0(zif[20], cdata[3], !cdata_en);		/* O8 */
	bufif0(zif[21], cdata[2], !cdata_en);		/* O8 */
	bufif0(zif[22], cdata[1], !cdata_en);		/* O8 */
	bufif0(zif[23], cdata[0], !cdata_en);		/* O8 */
	bufif0(zif[24], oe, low);			/* !OE */
	// Bottom of chip
	bufif0(zif[25], caddr[0], low);			/* A0 */
	bufif0(zif[26], caddr[1], low);			/* A1 */
	bufif0(zif[27], caddr[2], low);			/* A2 */
	bufif0(zif[28], caddr[3], low);			/* A3 */
	bufif0(zif[29], caddr[4], low);			/* A4 */
	bufif0(zif[30], caddr[5], low);			/* A5 */
	bufif0(zif[31], caddr[6], low);			/* A6 */
	bufif0(zif[32], caddr[7], low);			/* A7 */
	bufif0(zif[33], caddr[8], low);			/* A8 */
	bufif0(zif[34], low, low);			/* GND */
	bufif0(zif[35], caddr[9], low);			/* A9 */
	bufif0(zif[36], caddr[10], low);		/* A10 */
	bufif0(zif[37], caddr[11], low);		/* A11 */
	bufif0(zif[38], caddr[12], low);		/* A12 */
	bufif0(zif[39], caddr[13], low);		/* A13 */
	bufif0(zif[40], caddr[14], low);		/* A14 */
	bufif0(zif[41], caddr[15], low);		/* A15 */
	`ZIF_UNUSED(42)
	bufif0(zif[43], prog_pulse, low);		/* A15 */
	bufif0(zif[44], high, high);			/* VCC (>= 64) */
	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)	`ZIF_UNUSED(47)
	`ZIF_UNUSED(48)
`BOTTOMHALF_END
