/*
 *   TOP2049 Open Source programming suite
 *
 *   Cypress M8C In System Serial Programmer
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

module m8c_issp(data, ale, write, read, osc_in, zif);
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

	/* The M8C programmer context */
	`define ISSP_VEC_SIZE	22 /* bits */
	reg [1:0] issp_busy;				/* Busy state. We're busy, if bits are unequal */
	reg [7:0] issp_command;				/* Currently loaded command */
	reg [`ISSP_VEC_SIZE-1:0] issp_vector;		/* Currently loaded output vector */
	reg [`ISSP_VEC_SIZE-1:0] issp_input_mask;	/* Vector input bits mask */
	reg [`ISSP_VEC_SIZE-1:0] issp_input_vector;	/* Read data */
	reg [5:0] issp_vecbit;				/* Currently TXed/RXed bit */
	reg [7:0] issp_count;				/* General purpose counter */
	reg [3:0] issp_state;				/* Statemachine */

	/* The M8C programmer commands */
	`define ISSPCMD_NONE	0	/* No command loaded */
	`define ISSPCMD_POR	1	/* Perform a power-on-reset */
	`define ISSPCMD_PWROFF	2	/* Turn power off */
	`define ISSPCMD_SENDVEC	3	/* Send the vector */
	`define ISSPCMD_EXEC	4	/* Do an "execute" transfer */

	/* The M8C device signals */
	reg dut_sdata;
	reg dut_sdata_input;
	reg dut_sclk;
	reg dut_sclk_z;
	reg dut_vdd;
	`define VDD_ON		0
	`define VDD_OFF		1
	`define ZIF_SDATA	22	/* SDATA ZIF pin */

	assign low = 0;
	assign high = 1;

	initial begin
		issp_busy <= 0;
		issp_command <= 0;
		issp_vector <= 0;
		issp_vecbit <= `ISSP_VEC_SIZE;
		issp_state <= 0;
		dut_sdata <= 0;
		dut_sdata_input <= 1;
		dut_sclk <= 0;
		dut_sclk_z <= 1;
		dut_vdd <= `VDD_OFF;
		read_data <= 0;
	end

	/* The delay counter. Based on the 12MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	always @(posedge osc) begin
		if (delay_count == 0) begin
			if (issp_busy[0] != issp_busy[1]) begin
				/* busy0 != busy1 indicates that a command is running.
				 * Continue executing it... */

				if (issp_command == `ISSPCMD_POR) begin
					case (issp_state)
					0: begin
						/* Turn on power and wait vDDwait time */
						dut_vdd <= `VDD_ON;
						dut_sclk_z <= 1;
						dut_sclk <= 0;
						dut_sdata_input <= 1;
//						delay_count <= 24000 - 1; /* Wait 1ms */
						delay_count <= 12000 - 1;
//						delay_count <= 5000 - 1;
						issp_state <= 1;
					end
					1: begin
						if (zif[`ZIF_SDATA] == 1) begin
							issp_state <= 2;
							delay_count <= 6 - 1; /* Wait 250ns */
						end
					end
					2: begin
						if (zif[`ZIF_SDATA] == 0) begin
							issp_state <= 3;
							dut_sclk_z <= 0;
							dut_sclk <= 0;
							delay_count <= 6 - 1; /* Wait 250ns */
						end
					end
					3: begin
						if (issp_vecbit == 0) begin
							dut_sdata_input <= 1;
							issp_state <= 5;
						end else begin
							/* Ok, ready to send the next bit */
							dut_sclk_z <= 0;
							dut_sdata_input <= 0;
							dut_sdata <= issp_vector[issp_vecbit - 1];
							dut_sclk <= 1;
							issp_state <= 4;
							delay_count <= 6 - 1; /* Wait 250ns */
						end
					end
					4: begin
						dut_sclk <= 0;
						issp_state <= 3;
						issp_vecbit <= issp_vecbit - 1;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					5: begin
						/* We're done. */
						issp_busy[1] <= issp_busy[0];
						issp_vecbit <= `ISSP_VEC_SIZE;
						issp_state <= 0;
					end
					endcase
				end
				if (issp_command == `ISSPCMD_PWROFF) begin
					dut_vdd <= `VDD_OFF;
					dut_sdata_input <= 1;
					dut_sclk_z <= 1;
					/* We're done. */
					issp_busy[1] <= issp_busy[0];
				end
				if (issp_command == `ISSPCMD_SENDVEC) begin
					case (issp_state)
					0: begin
						dut_sclk_z <= 0;
						if (issp_input_mask[issp_vecbit - 1] == 0) begin
							/* Send bit */
							dut_sdata_input <= 0;
							dut_sdata <= issp_vector[issp_vecbit - 1];
						end
						dut_sclk <= 1;
						issp_state <= 1;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					1: begin
						if (issp_input_mask[issp_vecbit - 1] != 0) begin
							/* Receive bit */
							//FIXME?
							dut_sdata_input <= 1;
							issp_input_vector[issp_vecbit - 1] = zif[`ZIF_SDATA];
						end
						dut_sclk <= 0;
						issp_state <= 2;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					2: begin//FIXME?
						if (issp_vecbit == 0) begin
							/* We're done. */
							dut_sdata_input <= 1;
							issp_busy[1] <= issp_busy[0];
							issp_vecbit <= `ISSP_VEC_SIZE;
							issp_state <= 0;
						end else begin
							/* The next bit */
							issp_vecbit <= issp_vecbit - 1;
							issp_state <= 0;
						end
					end
					endcase
				end
				if (issp_command == `ISSPCMD_EXEC) begin
					case (issp_state)
					0: begin /* Init */
						dut_sdata_input <= 1;
						dut_sdata <= 0;
						dut_sclk_z <= 0;
						issp_count <= 40;
						issp_state <= 1;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					1: begin /* Wait 40 cycles, set clk=hi */
						dut_sclk <= 1;
						issp_state <= 2;
						issp_count <= issp_count - 1;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					2: begin /* Wait 40 cycles, set clk=lo */
						dut_sclk <= 0;
						if (issp_count == 0)
							issp_state <= 3;
						else
							issp_state <= 1;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					3: begin /* Wait for SDATA=0, set clk=hi */
						dut_sclk <= 1;
						dut_sdata_input <= 1;
						dut_sdata <= 0;
						if (zif[`ZIF_SDATA] == 0) begin
							/* Ok, got it. Now send 40 zeros. */
							issp_count <= 39;
							issp_state <= 5;
						end else begin
							issp_state <= 4;
						end
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					4: begin /* Wait for SDATA=0, set clk=lo */
						dut_sclk <= 0;
						issp_state <= 3;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					5: begin /* Send 40 zeros. set clk=lo */
						dut_sdata_input <= 0;
						dut_sclk <= 0;
						if (issp_count == 0)
							issp_state <= 7;
						else
							issp_state <= 6;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					6: begin /* Send 40 zeros. set clk=hi */
						dut_sclk <= 1;
						issp_count <= issp_count - 1;
						issp_state <= 5;
						delay_count <= 6 - 1; /* Wait 250ns */
					end
					7: begin /* finish */
						/* We're done. */
						issp_busy[1] <= issp_busy[0];
						dut_sdata_input <= 1;
						issp_state <= 0;
					end
					endcase
				end
			end
		end else begin
			delay_count <= delay_count - 1;
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin
			/* Data write */
			/* Unused */
		end
		8'h12: begin
			/* Load and execute command */
			issp_command <= data;
			issp_busy[0] <= ~issp_busy[1];
		end
		8'h13: begin
			/* Load vector low */
			issp_vector[7:0] <= data;
		end
		8'h14: begin
			/* Load vector med */
			issp_vector[15:8] <= data;
		end
		8'h15: begin
			/* Load vector high */
			issp_vector[21:16] <= data[5:0];
		end
		8'h16: begin
			/* Load input mask low */
			issp_input_mask[7:0] <= data;
		end
		8'h17: begin
			/* Load input mask med */
			issp_input_mask[15:8] <= data;
		end
		8'h18: begin
			/* Load input mask high */
			issp_input_mask[21:16] <= data[5:0];
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin
			/* Data read */
			/* Unused */
		end
		8'h12: begin
			/* Read status */
			read_data[0] <= (issp_busy[0] != issp_busy[1]);
		end
		8'h13: begin
			/* Read input vector low */
			read_data <= issp_input_vector[7:0];
		end
		8'h14: begin
			/* Read input vector med */
			read_data <= issp_input_vector[15:8];
		end
		8'h15: begin
			/* Read input vector high */
			read_data <= issp_input_vector[21:16];
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
	bufif0(zif[11], low, low);
	bufif0(zif[12], low, low);
	bufif0(zif[13], low, low);
	bufif0(zif[14], low, low);
	bufif0(zif[15], low, low);
	bufif0(zif[16], low, low);
	bufif0(zif[17], low, low);
	bufif0(zif[18], low, low);
	bufif0(zif[19], low, low);
	assign zif[20] = low;					/* GND */
	assign zif[21] = high;					/* VDD */
	bufif0(zif[`ZIF_SDATA], dut_sdata, dut_sdata_input);	/* SDATA */
	bufif0(zif[23], dut_sclk, dut_sclk_z);			/* SCLK */
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
