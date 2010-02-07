/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel Mega8 DIP28
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
module atmega8dip28(data, ale, write, read, zif);
	inout [7:0] data;
	input ale;
	input write;
	input read;
	inout [48:1] zif;

	// Read output-enable
	wire read_oe;
	// Signals to/from the DUT
	reg dut_oe, dut_wr, dut_xtal, dut_pagel, dut_busy;
	reg dut_bs1, dut_bs2;
	reg dut_xa0, dut_xa1;
	reg [7:0] dut_data;
	// Cached address value
	reg [7:0] address;
	// Cached read data
	reg [7:0] read_data;
	// Constant low
	wire low;
	// Debugging
	reg [7:0] test;

	assign low = 0;

	always @(negedge ale) begin
		address = data;
	end

	always @(posedge write) begin
		if (address == 8'h12) begin
//			if (data[6:0] == 1)
//				TODO
			if (data[6:0] == 2)
				dut_oe = data[7];
			if (data[6:0] == 3)
				dut_wr = data[7];
			if (data[6:0] == 4)
				dut_bs1 = data[7];
			if (data[6:0] == 5)
				dut_xa0 = data[7];
			if (data[6:0] == 6)
				dut_xa1 = data[7];
			if (data[6:0] == 7)
				dut_xtal = data[7];
//			if (data[6:0] == 8)
				// Unused
			if (data[6:0] == 9)
				dut_pagel = data[7];
			if (data[6:0] == 10)
				dut_bs2 = data[7];
		end
		if (address == 8'h1B) begin
			//TODO
		end
		if (address == 8'h1D) begin
			//TODO
		end
		if (address == 8'h11) begin
			//TODO
		end
		if (address == 8'h10) begin
			dut_data = data;
		end
	end

	always @(read or address or zif) begin
		read_data[0] = zif[24];
		read_data[1] = zif[25];
		read_data[2] = zif[26];
		read_data[3] = zif[27];
		read_data[4] = zif[28];
		read_data[5] = zif[29];
		read_data[6] = zif[33];
		read_data[7] = zif[34];
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
	bufif0(zif[13], low, low);
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