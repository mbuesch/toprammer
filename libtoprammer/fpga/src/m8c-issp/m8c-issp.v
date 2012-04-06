/*
 *   TOP2049 Open Source programming suite
 *
 *   Cypress M8C/M7C In System Serial Programmer
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2010-2011 Michael Buesch <m@bues.ch>
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
`define RUNTIME_ID	16'h0007
`define RUNTIME_REV	16'h01

module m8c_issp(data, ale, write, read, osc_in, zif);
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

	/* The M8C programmer context */
	`define ISSP_VEC_SIZE	22 /* bits */
	reg [1:0] issp_busy;				/* Busy state. We're busy, if bits are unequal */
	reg [7:0] issp_command;				/* Currently loaded command */
	reg [`ISSP_VEC_SIZE-1:0] issp_vector;		/* Currently loaded output vector */
	reg [5:0] issp_vecbit;				/* Currently TXed/RXed bit */
	reg [7:0] issp_count;				/* General purpose counter */
	reg [3:0] issp_state;				/* Statemachine */

	/* The M8C programmer commands */
	`define ISSPCMD_NONE	0	/* No command loaded */
	`define ISSPCMD_POR	1	/* Perform a power-on-reset */
	`define ISSPCMD_PWROFF	2	/* Turn power off */
	`define ISSPCMD_EXEC	3	/* Do an "execute" transfer */

	`define IS_BUSY		(issp_busy[0] != issp_busy[1])
	`define SET_FINISHED	issp_busy[1] <= issp_busy[0]

	/* The M8C device signals */
	wire sig_sdata;
	wire sig_sdata_input;
	wire sig_sclk;
	wire sig_sclk_z;
	reg dut_sdata;
	reg dut_sdata_input;
	reg dut_sclk;
	reg dut_sclk_z;
	reg dut_bitbang_disabled;
	reg dut_bitbang_sdata;
	reg dut_bitbang_sdata_input;
	reg dut_bitbang_sclk;
	reg dut_bitbang_sclk_z;
	reg dut_vdd;
	`define VDD_ON		1
	`define VDD_OFF		0
	`define ZIF_SDATA	22	/* SDATA ZIF pin */

	assign low = 0;
	assign high = 1;

	/* The delay counter. Based on the 24MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	`define DELAY_250NS	6 - 1		/* 250 ns */
	`define DELAY_1US	24 - 1		/* 1 us */
	`define DELAY_1MS	24000 - 1	/* 1 ms */
	`define DELAY_1P5MS	36000 - 1	/* 1.5 ms */
	`define DELAY_2MS	48000 - 1	/* 2 ms */

	initial begin
		address <= 0;
		read_data <= 0;

		issp_busy <= 0;
		issp_command <= 0;
		issp_vector <= 0;
		issp_vecbit <= 0;
		issp_count <= 0;
		issp_state <= 0;

		dut_sdata <= 0;
		dut_sdata_input <= 1;
		dut_sclk <= 0;
		dut_sclk_z <= 1;
		dut_vdd <= `VDD_OFF;

		dut_bitbang_disabled <= 0;
		dut_bitbang_sdata <= 0;
		dut_bitbang_sdata_input <= 1;
		dut_bitbang_sclk <= 0;
		dut_bitbang_sclk_z <= 1;

		delay_count <= 0;
	end

	always @(posedge osc) begin
		if (delay_count == 0 && `IS_BUSY) begin
			case (issp_command)
			`ISSPCMD_POR: begin
				case (issp_state)
				0: begin
					/* Turn on power and wait vDDwait time */
					dut_vdd <= `VDD_ON;
					dut_bitbang_disabled <= 1;
					dut_sclk_z <= 1;
					dut_sclk <= 0;
					dut_sdata_input <= 1;
					delay_count <= `DELAY_1MS;	/* TvDDwait */
					issp_state <= 1;
				end
				1: begin
					dut_sclk_z <= 0;
					dut_sclk <= 0;
					if (zif[`ZIF_SDATA] == 0) begin
						issp_state <= 2;
						issp_vecbit <= `ISSP_VEC_SIZE;
					end
//					delay_count <= `DELAY_250NS;
				end
				2: begin
					if (issp_vecbit == 0) begin
						issp_state <= 4;
					end else begin
						/* Ok, ready to send the next bit */
						dut_sdata_input <= 0;
						dut_sdata <= issp_vector[issp_vecbit - 1];
						dut_sclk <= 1;
						issp_state <= 3;
					end
					delay_count <= `DELAY_250NS;
				end
				3: begin
					dut_sclk <= 0;
					issp_state <= 2;
					issp_vecbit <= issp_vecbit - 1;
					delay_count <= `DELAY_250NS;
				end
				4: begin
					/* We're done. */
					`SET_FINISHED;
					dut_bitbang_disabled <= 0;
					dut_sclk <= 0;
					dut_sdata_input <= 1;
					issp_state <= 0;
				end
				endcase
			end
			`ISSPCMD_PWROFF: begin
				dut_vdd <= `VDD_OFF;
				dut_bitbang_disabled <= 0;
				dut_sdata <= 0;
				dut_sdata_input <= 1;
				dut_sclk <= 0;
				dut_sclk_z <= 1;
				issp_state <= 0;
				delay_count <= 0;
				/* We're done. */
				`SET_FINISHED;
			end
			`ISSPCMD_EXEC: begin
				case (issp_state)
				0: begin /* Init */
					dut_bitbang_disabled <= 1;
					dut_sdata <= 0;
					dut_sdata_input <= 1;
					dut_sclk_z <= 0;
					dut_sclk <= 0;
					issp_count <= 10;
					issp_state <= 1;
				end
				1: begin /* Wait for SDATA=1 */
					if (zif[`ZIF_SDATA]) begin
						issp_state <= 5; /* goto wait-for-SDATA=0 */
					end else begin
						delay_count <= `DELAY_1US;
						issp_count <= issp_count - 1;
						issp_state <= 2;
					end
				end
				2: begin
					if (issp_count == 0) begin
						/* Timeout */
						issp_state <= 3; /* Send 33 CLKs */
						issp_count <= 33;
					end else begin
						issp_state <= 1;
					end
				end
				3: begin /* Send 33 CLKs */
					dut_sclk <= 1;
					issp_count <= issp_count - 1;
					delay_count <= `DELAY_250NS;
					issp_state <= 4;
				end
				4: begin
					dut_sclk <= 0;
					if (issp_count == 0) begin
						/* Sent all */
						if (zif[`ZIF_SDATA]) begin
							issp_state <= 5; /* goto wait-for-SDATA=0 */
						end else begin
							/* goto send-50-CLKs */
							issp_state <= 6;
							issp_count <= 50;
						end
					end else begin
						issp_state <= 3;
					end
					delay_count <= `DELAY_250NS;
				end
				5: begin /* Wait for SDATA=0 */
					if (zif[`ZIF_SDATA] == 0) begin
						issp_state <= 6;
						issp_count <= 50;
					end else begin
						issp_state <= 5;
					end
					delay_count <= `DELAY_250NS;
				end
				6: begin /* Send 50 CLKs */
					dut_sclk <= 1;
					issp_count <= issp_count - 1;
					delay_count <= `DELAY_250NS;
					issp_state <= 7;
				end
				7: begin
					dut_sclk <= 0;
					if (issp_count == 0) begin
						issp_state <= 8; /* done */
					end else begin
						issp_state <= 6;
					end
					delay_count <= `DELAY_250NS;
				end
				8: begin /* finish */
					/* We're done. */
					dut_bitbang_disabled <= 0;
					issp_state <= 0;
					`SET_FINISHED;
				end
				endcase
			end
			endcase
		end else begin
			if (delay_count) begin
				delay_count <= delay_count - 1;
			end
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin
			/* Bitbanging */
			dut_bitbang_sdata <= data[0];
			dut_bitbang_sdata_input <= data[1];
			dut_bitbang_sclk <= data[2];
			dut_bitbang_sclk_z <= data[3];
		end
		8'h11: begin
			/* Load and execute command */
			issp_command <= data;
			issp_busy[0] <= ~issp_busy[1];
		end
		8'h12: begin
			/* Load vector low */
			issp_vector[7:0] <= data;
		end
		8'h13: begin
			/* Load vector med */
			issp_vector[15:8] <= data;
		end
		8'h14: begin
			/* Load vector high */
			issp_vector[21:16] <= data[5:0];
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin
			/* Read status */
			read_data[0] <= issp_busy[0];
			read_data[1] <= issp_busy[1];

			read_data[2] <= issp_state[0];
			read_data[3] <= issp_state[1];
			read_data[4] <= issp_state[2];

			read_data[5] <= zif[`ZIF_SDATA];
			read_data[6] <= 0;
			read_data[7] <= 0;
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

	assign sig_sdata = dut_bitbang_disabled ? dut_sdata : dut_bitbang_sdata;
	assign sig_sdata_input = dut_bitbang_disabled ? dut_sdata_input : dut_bitbang_sdata_input;
	assign sig_sclk = dut_bitbang_disabled ? dut_sclk : dut_bitbang_sclk;
	assign sig_sclk_z = dut_bitbang_disabled ? dut_sclk_z : dut_bitbang_sclk_z;

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
	bufif0(zif[20], low, low);				/* GND */
	bufif0(zif[21], high, low);				/* VDD */
	bufif0(zif[`ZIF_SDATA], sig_sdata, sig_sdata_input);	/* SDATA */
	bufif0(zif[23], sig_sclk, sig_sclk_z);			/* SCLK */
	bufif0(zif[24], dut_vdd, low);				/* VDDen */
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
