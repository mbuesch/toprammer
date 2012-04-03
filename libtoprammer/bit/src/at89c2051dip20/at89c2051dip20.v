/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel AT89C2051 DIP20
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2010 Guido
 *   Copyright (c) 2010 Michael Buesch <m@bues.ch>
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
`define RUNTIME_ID	16'h0005
`define RUNTIME_REV	16'h01

module at89c2051dip20(data, ale, write, read, osc_in, zif);
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

	/* Programmer context */
	reg [1:0] prog_busy;
	reg [3:0] prog_command;
	reg [3:0] prog_state;
	reg [3:0] prog_count;
	reg prog_err;

	/* DUT signals */
	reg [7:0] dut_data;
	reg dut_p33;
	reg dut_p34;
	reg dut_p35;
	reg dut_p37;
	reg dut_ia;	/* Increment Address */
	reg dut_prog;
	reg dut_vpp;


	assign low = 0;
	assign high = 1;

	initial begin
		prog_busy <= 0;
		prog_command <= 0;
		prog_state <= 0;
		prog_err <= 0;
		prog_count <= 0;
		dut_data <= 0;
		dut_p33 <= 0;
		dut_p34 <= 0;
		dut_p35 <= 0;
		dut_p37 <= 0;
		dut_ia <= 0;
		dut_prog <= 0;
		dut_vpp <= 0;
	end

	/* The delay counter. Based on the 24MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	always @(posedge osc) begin
		if (delay_count == 0) begin
			if (prog_busy[0] != prog_busy[1]) begin
				/* busy0 != busy1 indicates that a command is running.
				* Continue executing it... */
				case (prog_command)
				1: begin /* Set P3.2 after init */
					dut_prog <= 1;
					prog_busy[1] <= prog_busy[0];
				end
				2: begin /* clear P3.2 before shutdown */
					dut_prog <= 0;
					prog_busy[1] <= prog_busy[0];
				end
				3: begin /* programm byte */
					case (prog_state)
					0: begin /* pulse */
						delay_count <= 24;
						dut_prog <= 0;
						prog_state <= 1;
						prog_err <= 0;
					end
					1: begin /* raise dut_prog */
						dut_prog <= 1;
						prog_state <= 2;
						prog_count <= 12;
						delay_count <= 2;
					end
					2: begin /* wait for ready == 1 */
						if (zif[17] == 0) begin
							delay_count <= 4800; /* each 200 us */
							prog_count <= prog_count - 1;
							if (prog_count == 0) begin
								prog_err <= 1;
								prog_state <= 3;
							end
						end
						else begin
							prog_state <= 3;
							delay_count <= 24;
						end
					end
					3: begin /* finish */
						prog_state <= 0;
						prog_busy[1] <= prog_busy[0];
					end
					endcase
				end
				4: begin /* chip erase */
					case (prog_state)
					0: begin /* start erasing */
						delay_count <= 24000; /* 1 ms each */
						prog_count <= 10;
						dut_prog <= 0;
						prog_state <= 1;
						prog_err <= 0;
					end
					1: begin /* loop */
						prog_count <= prog_count - 1;
						if (prog_count == 0) begin
							dut_prog <= 1;
							prog_state <= 0;
							prog_busy[1] <= prog_busy[0];
						end
						else begin
							delay_count <= 24000;
						end
					end
					endcase
				end
				5: begin /* set dut_vpp */
					dut_vpp <= 1;
					prog_busy[1] <= prog_busy[0];
				end
				6: begin /* clear dut_vpp */
					dut_vpp <= 0;
					prog_busy[1] <= prog_busy[0];
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
		8'h16: begin
			/* Set P33, P34, P35; IA */
			dut_p33 <= data[0];
			dut_p34 <= data[1];
			dut_p35 <= data[2];
			dut_p37 <= data[2];
			dut_ia <= data[3];
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin
			/* Data read */
			read_data[7:0] <= zif[33:26];
		end
		8'h12: begin
			/* Read status */
			read_data[0] <= (prog_busy[0] != prog_busy[1]);
			read_data[1] <= prog_err;
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
	bufif0(zif[15], low, dut_vpp);		/* VPP/Reset */
	bufif0(zif[16], low, low);		/* P3.0 */
	bufif0(zif[17], low, high);		/* P3.1 */
	bufif0(zif[18], low, low);		/* XTAL2 */
	bufif0(zif[19], dut_ia, low);		/* XTAL1 */
	bufif0(zif[20], dut_prog, low);		/* P3.2 */
	bufif0(zif[21], dut_p33, low);		/* P3.3 */
	bufif0(zif[22], dut_p34, low); 		/* P3.4 */
	bufif0(zif[23], dut_p35, low);		/* P3.5 */
	bufif0(zif[24], low, low);		/* GND */
	bufif0(zif[25], dut_p37, low);		/* P3.7 */
	bufif0(zif[26], dut_data[0], !dut_p34);	/* P1.0 */
	bufif0(zif[27], dut_data[1], !dut_p34);	/* P1.1 */
	bufif0(zif[28], dut_data[2], !dut_p34);	/* P1.2 */
	bufif0(zif[29], dut_data[3], !dut_p34);	/* P1.3 */
	bufif0(zif[30], dut_data[4], !dut_p34);	/* P1.4 */
	bufif0(zif[31], dut_data[5], !dut_p34);	/* P1.5 */
	bufif0(zif[32], dut_data[6], !dut_p34);	/* P1.6 */
	bufif0(zif[33], dut_data[7], !dut_p34);	/* P1.7 */
	bufif0(zif[34], high, low);		/* VCC */
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
