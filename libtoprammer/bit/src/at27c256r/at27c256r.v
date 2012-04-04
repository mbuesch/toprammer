/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel AT27C256R EPROM
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

/* The runtime ID and revision. */
`define RUNTIME_ID	16'h000C
`define RUNTIME_REV	16'h01

module at27c256r(data, ale, write, read, osc_in, zif);
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

	/* Interface to the chip */
	reg [7:0] chip_data;
	reg chip_data_en;
	reg [14:0] chip_addr;
	reg chip_ce;		/* !CE */
	reg chip_prog_ce;	/* !CE prog pulse */
	reg chip_prog_en;
	wire chip_ce_wire;
	reg chip_oe;		/* !OE */

	assign chip_ce_wire = chip_prog_en ? chip_prog_ce : chip_ce;

	reg [1:0] prog_busy;	/* busy flag */
	reg [3:0] prog_state;	/* prog state */

	wire low, high;		/* Constant lo/hi */
	assign low = 0;
	assign high = 1;

	/* The delay counter. Based on the 24MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	initial begin
		address <= 0;
		read_data <= 0;
		delay_count <= 0;
		chip_data <= 0;
		chip_data_en <= 0;
		chip_addr <= 0;
		chip_ce <= 1;
		chip_prog_ce <= 1;
		chip_prog_en <= 0;
		chip_oe <= 1;
		prog_busy <= 0;
		prog_state <= 0;
	end

	`define SET_BUSY	prog_busy[0] <= !prog_busy[1]
	`define IS_BUSY		prog_busy[0] != prog_busy[1]
	`define FINISH		prog_busy[1] <= prog_busy[0]

	`define DELAY_100US	delay_count <= 2400 - 1		/* 100uS */

	always @(posedge osc) begin
		if (delay_count == 0) begin
			if (`IS_BUSY) begin
				case (prog_state)
				0: begin
					chip_prog_ce <= 0;
					prog_state <= 1;
					`DELAY_100US;
				end
				1: begin
					chip_prog_ce <= 1;
					prog_state <= 0;
					`FINISH;
				end
				endcase
			end
		end else begin
			delay_count <= delay_count - 1;
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin /* Address low write */
			chip_addr[7:0] <= data[7:0];
		end
		8'h11: begin /* Address high write */
			chip_addr[14:8] <= data[6:0];
		end
		8'h12: begin /* Data pins write */
			chip_data[7:0] <= data[7:0];
		end
		8'h13: begin /* Flags write */
			chip_data_en <= data[0];
			chip_prog_en <= data[1];
			chip_ce <= data[2];
			chip_oe <= data[3];
		end
		8'h14: begin /* Perform prog pulse */
			`SET_BUSY;
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin /* Data pins read */
			read_data[2:0] <= zif[23:21];
			read_data[7:3] <= zif[29:25];
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
	bufif0(zif[11], low, high);			/* VPP */
	bufif0(zif[12], chip_addr[12], low);		/* A12 */
	bufif0(zif[13], chip_addr[7], low);		/* A7 */
	bufif0(zif[14], chip_addr[6], low);		/* A6 */
	bufif0(zif[15], chip_addr[5], low);		/* A5 */
	bufif0(zif[16], chip_addr[4], low);		/* A4 */
	bufif0(zif[17], chip_addr[3], low);		/* A3 */
	bufif0(zif[18], chip_addr[2], low);		/* A2 */
	bufif0(zif[19], chip_addr[1], low);		/* A1 */
	bufif0(zif[20], chip_addr[0], low);		/* A0 */
	bufif0(zif[21], chip_data[0], !chip_data_en);	/* O0 */
	bufif0(zif[22], chip_data[1], !chip_data_en);	/* O1 */
	bufif0(zif[23], chip_data[2], !chip_data_en);	/* O2 */
	bufif0(zif[24], low, low);			/* GND */
	bufif0(zif[25], chip_data[3], !chip_data_en);	/* O3 */
	bufif0(zif[26], chip_data[4], !chip_data_en);	/* O4 */
	bufif0(zif[27], chip_data[5], !chip_data_en);	/* O5 */
	bufif0(zif[28], chip_data[6], !chip_data_en);	/* O6 */
	bufif0(zif[29], chip_data[7], !chip_data_en);	/* O7 */
	bufif0(zif[30], chip_ce_wire, low);		/* !CE */
	bufif0(zif[31], chip_addr[10], low);		/* A10 */
	bufif0(zif[32], chip_oe, low);			/* !OE */
	bufif0(zif[33], chip_addr[11], low);		/* A11 */
	bufif0(zif[34], chip_addr[9], low);		/* A9 */
	bufif0(zif[35], chip_addr[8], low);		/* A8 */
	bufif0(zif[36], chip_addr[13], low);		/* A13 */
	bufif0(zif[37], chip_addr[14], low);		/* A14 */
	bufif0(zif[38], high, low);			/* VCC */
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
