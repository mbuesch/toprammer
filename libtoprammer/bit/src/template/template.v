/*
 *   TOP2049 Open Source programming suite
 *
 *   XXXXXXXXXXXXXXXX
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2011 Michael Buesch <mb@bu3sch.de>
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
`define RUNTIME_ID	16'hTODO   Get an unused ID from the file "RUNTIME_IDS"
`define RUNTIME_REV	16'h01

module template(data, ale, write, read, osc_in, zif);
	inout [7:0] data;
	input ale;
	input write;
	input read;
	input osc_in; /* 24MHz oscillator */
	inout [48:1] zif;

	/* Interface to the microcontroller */
	wire read_oe;		/* Read output-enable */
	reg [7:0] address;	/* Cached address value */
	reg [7:0] read_data;	/* Cached read data */

	wire low, high;		/* Constant lo/hi */

	assign low = 0;
	assign high = 1;

	/* The delay counter. Based on the 24MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	always @(posedge osc) begin
		if (delay_count == 0) begin
			/* TODO */
		end else begin
			delay_count <= delay_count - 1;
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin /* Bulk write */
			/* TODO */
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin /* Bulk read */
			/* TODO */
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
	bufif0(zif[11], low, low);
	bufif0(zif[12], low, low);
	bufif0(zif[13], low, low);
	bufif0(zif[14], low, low);
	bufif0(zif[15], low, low);
	bufif0(zif[16], low, low);
	bufif0(zif[17], low, low);
	bufif0(zif[18], low, low);
	bufif0(zif[19], low, low);
	bufif0(zif[20], low, low);
	bufif0(zif[21], low, low);
	bufif0(zif[22], low, low);
	bufif0(zif[23], low, low);
	bufif0(zif[24], low, low);
	bufif0(zif[25], low, low);
	bufif0(zif[26], low, low);
	bufif0(zif[27], low, low);
	bufif0(zif[28], low, low);
	bufif0(zif[29], low, low);
	bufif0(zif[30], low, low);
	bufif0(zif[31], low, low);
	bufif0(zif[32], low, low);
	bufif0(zif[33], low, low);
	bufif0(zif[34], low, low);
	bufif0(zif[35], low, low);
	bufif0(zif[36], low, low);
	bufif0(zif[37], low, low);
	bufif0(zif[38], low, low);
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
