/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel Mega8 DIP28
 *   Atmel Mega88 DIP28
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2010 Michael Buesch <mb@bu3sch.de>
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

/* The runtime ID and revision. */
`define RUNTIME_ID	16'h0003
`define RUNTIME_REV	16'h01

module atmega8dip28(data, ale, write, read, zif);
	inout [7:0] data;
	input ale;
	input write;
	input read;
	inout [48:1] zif;

	// Read output-enable
	wire read_oe;
	// Signals to/from the DUT
	reg dut_oe, dut_wr, dut_xtal, dut_pagel;
	reg dut_bs1, dut_bs2;
	reg dut_xa0, dut_xa1;
	reg [7:0] dut_data;
	// Cached address value
	reg [7:0] address;
	// Cached read data
	reg [7:0] read_data;
	// Constant lo/hi
	wire low, high;

	assign low = 0;
	assign high = 1;

	always @(negedge ale) begin
		address <= data;
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin
			/* Data write */
			dut_data <= data;
		end
		8'h11: begin
			/* Nothing */
		end
		8'h12: begin
			/* Control pin access */
			case (data[6:0])
			1: begin
				/* Unused */
			end
			2: begin
				dut_oe <= data[7];
			end
			3: begin
				dut_wr <= data[7];
			end
			4: begin
				dut_bs1 <= data[7];
			end
			5: begin
				dut_xa0 <= data[7];
			end
			6: begin
				dut_xa1 <= data[7];
			end
			7: begin
				dut_xtal <= data[7];
			end
			8: begin
				/* Unused */
			end
			9: begin
				dut_pagel <= data[7];
			end
			10: begin
				dut_bs2 <= data[7];
			end
			endcase
		end
		8'h1B: begin
			/* Nothing */
		end
		8'h1D: begin
			/* Nothing */
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin
			/* Data read */
			read_data[5:0] <= zif[29:24];
			read_data[7:6] <= zif[34:33];
		end
		8'h12: begin
			/* Status read */
			read_data[0] <= zif[13];	/* RDY */
			read_data[7:1] <= 0;
		end

		8'hFD: read_data <= `RUNTIME_ID & 16'hFF;
		8'hFE: read_data <= (`RUNTIME_ID >> 8) & 16'hFF;
		8'hFF: read_data <= `RUNTIME_REV;
		endcase
	end

	assign read_oe = !read && address[4];

	bufif0(zif[1], low, low);
	bufif0(zif[2], low, low);
	bufif0(zif[3], low, low);
	bufif0(zif[4], low, low);
	bufif0(zif[5], low, low);
	bufif0(zif[6], low, low);
	bufif0(zif[7], low, low);
	bufif0(zif[8], low, low);
	bufif0(zif[9], low, low);
	bufif0(zif[10], low, low);
	bufif0(zif[11], low, high);		/* PC6, /RESET */
	bufif0(zif[12], low, low);		/* PD0 */
	bufif0(zif[13], low, high);		/* PD1, RDY/BSY */
	bufif0(zif[14], dut_oe, low);		/* PD2, /OE */
	bufif0(zif[15], dut_wr, low);		/* PD3, /WR */
	bufif0(zif[16], dut_bs1, low);		/* PD4, BS1 */
	bufif0(zif[17], high, low);		/* VCC */
	bufif0(zif[18], low, low);		/* GND */
	bufif0(zif[19], dut_xtal, low);		/* PB6, XTAL1 */
	bufif0(zif[20], low, high);		/* PB7, XTAL2 */
	bufif0(zif[21], dut_xa0, low);		/* PD5, XA0 */
	bufif0(zif[22], dut_xa1, low);		/* PD6, XA1 */
	bufif0(zif[23], dut_pagel, low);	/* PD7, PAGEL */
	bufif0(zif[24], dut_data[0], !dut_oe);	/* PB0, DATA0 */
	bufif0(zif[25], dut_data[1], !dut_oe);	/* PB1, DATA1 */
	bufif0(zif[26], dut_data[2], !dut_oe);	/* PB2, DATA2 */
	bufif0(zif[27], dut_data[3], !dut_oe);	/* PB3, DATA3 */
	bufif0(zif[28], dut_data[4], !dut_oe);	/* PB4, DATA4 */
	bufif0(zif[29], dut_data[5], !dut_oe);	/* PB5, DATA5 */
	bufif0(zif[30], high, low);		/* AVCC */
	bufif0(zif[31], low, high);		/* AREF */
	bufif0(zif[32], low, low);		/* GND */
	bufif0(zif[33], dut_data[6], !dut_oe);	/* PC0, DATA6 */
	bufif0(zif[34], dut_data[7], !dut_oe);	/* PC1, DATA7 */
	bufif0(zif[35], dut_bs2, low);		/* PC2, BS2 */
	bufif0(zif[36], low, low);		/* PC3 */
	bufif0(zif[37], low, low);		/* PC4 */
	bufif0(zif[38], low, low);		/* PC5 */
	bufif0(zif[39], low, low);
	bufif0(zif[40], low, low);
	bufif0(zif[41], low, low);
	bufif0(zif[42], low, low);
	bufif0(zif[43], low, low);
	bufif0(zif[44], low, low);
	bufif0(zif[45], low, low);
	bufif0(zif[46], low, low);
	bufif0(zif[47], low, low);
	bufif0(zif[48], low, low);

	bufif1(data[0], read_data[0], read_oe);
	bufif1(data[1], read_data[1], read_oe);
	bufif1(data[2], read_data[2], read_oe);
	bufif1(data[3], read_data[3], read_oe);
	bufif1(data[4], read_data[4], read_oe);
	bufif1(data[5], read_data[5], read_oe);
	bufif1(data[6], read_data[6], read_oe);
	bufif1(data[7], read_data[7], read_oe);
endmodule
