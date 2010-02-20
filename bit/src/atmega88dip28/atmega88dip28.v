/*
 *   TOP2049 Open Source programming suite
 *
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

module atmega88dip28(data, ale, write, read, zif);
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
	// Debugging
	reg [7:0] test;

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
		8'h16: begin
			/* Raw ZIF pin read access */
			read_data <= zif[8:1];
		end
		8'h17: begin
			/* Raw ZIF pin read access */
			read_data <= zif[16:9];
		end
		8'h18: begin
			/* Raw ZIF pin read access */
			read_data <= zif[24:17];
		end
		8'h19: begin
			/* Raw ZIF pin read access */
			read_data <= zif[32:25];
		end
		8'h1A: begin
			/* Raw ZIF pin read access */
			read_data <= zif[40:33];
		end
		8'h1B: begin
			/* Raw ZIF pin read access */
			read_data <= zif[48:41];
		end
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
	bufif0(zif[11], low, low);
	bufif0(zif[12], low, low);
	bufif0(zif[13], low, high);
	bufif0(zif[14], dut_oe, low);
	bufif0(zif[15], dut_wr, low);
	bufif0(zif[16], dut_bs1, low);
	bufif0(zif[17], low, low);
	bufif0(zif[18], low, low);
	bufif0(zif[19], dut_xtal, low);
	bufif0(zif[20], low, low);
	bufif0(zif[21], dut_xa0, low);
	bufif0(zif[22], dut_xa1, low);
	bufif0(zif[23], dut_pagel, low);
	bufif0(zif[24], dut_data[0], !dut_oe);
	bufif0(zif[25], dut_data[1], !dut_oe);
	bufif0(zif[26], dut_data[2], !dut_oe);
	bufif0(zif[27], dut_data[3], !dut_oe);
	bufif0(zif[28], dut_data[4], !dut_oe);
	bufif0(zif[29], dut_data[5], !dut_oe);
	bufif0(zif[30], low, low);
	bufif0(zif[31], low, low);
	bufif0(zif[32], low, low);
	bufif0(zif[33], dut_data[6], !dut_oe);
	bufif0(zif[34], dut_data[7], !dut_oe);
	bufif0(zif[35], dut_bs2, low);
	bufif0(zif[36], low, low);
	bufif0(zif[37], low, low);
	bufif0(zif[38], low, low);
	bufif0(zif[39], low, low);
	bufif0(zif[40], low, low);
	bufif0(zif[41], test[0], low);
	bufif0(zif[42], test[1], low);
	bufif0(zif[43], test[2], low);
	bufif0(zif[44], test[3], low);
	bufif0(zif[45], test[4], low);
	bufif0(zif[46], test[5], low);
	bufif0(zif[47], test[6], low);
	bufif0(zif[48], test[7], low);

	bufif1(data[0], read_data[0], read_oe);
	bufif1(data[1], read_data[1], read_oe);
	bufif1(data[2], read_data[2], read_oe);
	bufif1(data[3], read_data[3], read_oe);
	bufif1(data[4], read_data[4], read_oe);
	bufif1(data[5], read_data[5], read_oe);
	bufif1(data[6], read_data[6], read_oe);
	bufif1(data[7], read_data[7], read_oe);
endmodule
