/*
 *   TOP2049 Open Source programming suite
 *
 *   M2764A EPROM
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

module m2764a(data, ale, write, read, osc_in, zif);
	inout [7:0] data;
	input ale;
	input write;
	input read;
	input osc_in; /* 12MHz oscillator */
	inout [48:1] zif;

	/* Interface to the microcontroller */
	wire read_oe;		/* Read output-enable */
	reg [7:0] address;	/* Cached address value */
	reg [7:0] read_data;	/* Cached read data */

	wire low, high;		/* Constant lo/hi */

	/* Programmer context */
	reg [1:0] prog_busy;
	reg [3:0] prog_command;
	reg [3:0] prog_state;
	reg [7:0] prog_pulselen;
	reg [7:0] prog_count;
	`define PROG_PPULSE	1

	/* DUT signals */
	reg [12:0] dut_addr;
	reg [7:0] dut_data;
	reg dut_E;
	reg dut_P;
	reg dut_G;

	assign low = 0;
	assign high = 1;

	initial begin
		prog_busy <= 0;
		prog_command <= 0;
		prog_state <= 0;
		prog_pulselen <= 0;
		prog_count <= 0;
		dut_addr <= 0;
		dut_data <= 0;
		dut_E <= 1;
		dut_P <= 1;
		dut_G <= 1;
	end

	/* The delay counter. Based on the 12MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	always @(posedge osc) begin
		if (delay_count == 0) begin
			if (prog_busy[0] != prog_busy[1]) begin
				/* busy0 != busy1 indicates that a command is running.
				 * Continue executing it... */

				case (prog_command)
				`PROG_PPULSE: begin
					case (prog_state)
					0: begin /* Init */
						dut_P <= 0;
						prog_count <= prog_pulselen - 1;
						prog_state <= 1;
						delay_count <= 24000 - 2;
					end
					1: begin /* Delay loop */
						if (prog_count == 0) begin
							/* Done */
							dut_P <= 1;
							prog_state <= 0;
							prog_busy[1] <= prog_busy[0];
						end else begin
							prog_state <= 2;
							delay_count <= 24000 - 2;
						end
					end
					2: begin
						prog_count <= prog_count - 1;
						prog_state <= 1;
					end
					endcase
				end
				endcase
			end
		end else begin
			delay_count <= delay_count - 1;
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin
			/* Data write */
			dut_data <= data;
		end
		8'h12: begin
			/* Run a command. */
			prog_command <= data;
			prog_busy[0] <= ~prog_busy[1];
		end
		8'h13: begin
			/* Set addr low */
			dut_addr[7:0] <= data;
		end
		8'h14: begin
			/* Set addr high */
			dut_addr[12:8] <= data[4:0];
		end
		8'h15: begin
			/* Set P pulse len */
			prog_pulselen <= data;
		end
		8'h16: begin
			/* Set E/G */
			dut_E <= data[0];
			dut_G <= data[1];
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin
			/* Data read */
			read_data[2:0] <= zif[23:21];
			read_data[7:3] <= zif[29:25];
		end
		8'h12: begin
			/* Read status */
			read_data[0] <= (prog_busy[0] != prog_busy[1]);
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
	bufif0(zif[11], low, high);		/* VPP */
	bufif0(zif[12], dut_addr[12], low);	/* A12 */
	bufif0(zif[13], dut_addr[7], low);	/* A7 */
	bufif0(zif[14], dut_addr[6], low);	/* A6 */
	bufif0(zif[15], dut_addr[5], low);	/* A5 */
	bufif0(zif[16], dut_addr[4], low);	/* A4 */
	bufif0(zif[17], dut_addr[3], low);	/* A3 */
	bufif0(zif[18], dut_addr[2], low);	/* A2 */
	bufif0(zif[19], dut_addr[1], low);	/* A1 */
	bufif0(zif[20], dut_addr[0], low);	/* A0 */
	bufif0(zif[21], dut_data[0], !dut_G);	/* Q0 */
	bufif0(zif[22], dut_data[1], !dut_G);	/* Q1 */
	bufif0(zif[23], dut_data[2], !dut_G);	/* Q2 */
	bufif0(zif[24], low, low);		/* Vss */
	bufif0(zif[25], dut_data[3], !dut_G);	/* Q3 */
	bufif0(zif[26], dut_data[4], !dut_G);	/* Q4 */
	bufif0(zif[27], dut_data[5], !dut_G);	/* Q5 */
	bufif0(zif[28], dut_data[6], !dut_G);	/* Q6 */
	bufif0(zif[29], dut_data[7], !dut_G);	/* Q7 */
	bufif0(zif[30], dut_E, low);		/* E */
	bufif0(zif[31], dut_addr[10], low);	/* A10 */
	bufif0(zif[32], dut_G, low);		/* G */
	bufif0(zif[33], dut_addr[11], low);	/* A11 */
	bufif0(zif[34], dut_addr[9], low);	/* A9 */
	bufif0(zif[35], dut_addr[8], low);	/* A8 */
	bufif0(zif[36], low, low);		/* NC */
	bufif0(zif[37], dut_P, low);		/* P */
	bufif0(zif[38], high, low);		/* Vcc */
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
