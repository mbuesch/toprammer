/*
 *   TOP2049 Open Source programming suite
 *
 *   HM62256 SRAM
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2011 Michael Buesch <m@bues.ch>
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
`define RUNTIME_ID	16'h000A
`define RUNTIME_REV	16'h01

module hm62256dip28(data, ale, write, read, zif);
	inout [7:0] data;
	input ale;
	input write;
	input read;
	inout [48:1] zif;

	/* Interface to the microcontroller */
	wire read_oe;		/* Read output-enable */
	reg [7:0] address;	/* Cached address value */
	reg [7:0] read_data;	/* Cached read data */

	/* Chip (DUT) signals */
	reg [14:0] dut_addr;
	reg [7:0] dut_data;
	reg dut_ce;
	reg dut_oe;
	reg dut_we;

	wire low, high;		/* Constant lo/hi */

	assign low = 0;
	assign high = 1;

	always @(posedge write) begin
		case (address)
		8'h10: begin /* Bulk write */
			dut_data <= data;
		end
		8'h11: begin /* /CE, /OE, /WE */
			dut_ce <= data[0];
			dut_oe <= data[1];
			dut_we <= data[2];
		end
		8'h12: begin /* Addr byte 0 */
			dut_addr[7:0] <= data[7:0];
		end
		8'h13: begin /* Addr byte 1 */
			dut_addr[14:8] <= data[6:0];
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin /* Bulk read */
			read_data[0] <= zif[21];
			read_data[1] <= zif[22];
			read_data[2] <= zif[23];
			read_data[3] <= zif[25];
			read_data[4] <= zif[26];
			read_data[5] <= zif[27];
			read_data[6] <= zif[28];
			read_data[7] <= zif[29];
		end

		8'hFD: read_data <= `RUNTIME_ID & 16'hFF;
		8'hFE: read_data <= (`RUNTIME_ID >> 8) & 16'hFF;
		8'hFF: read_data <= `RUNTIME_REV;
		endcase
	end

	always @(negedge ale) begin
		address <= data;
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
