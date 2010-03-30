/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel Tiny13 DIP8
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

module attiny13dip8(data, ale, write, read, osc_in, zif);
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

	/* Programmer context */
	reg [1:0] prog_busy;
	reg [7:0] prog_command;
	reg [7:0] prog_state;
	reg [7:0] prog_count;
	`define CMD_SENDINSTR	1
	reg dut_sdi;
	reg dut_sii;
	reg dut_sci_manual;
	reg dut_sci_auto;
	wire dut_sci;
	reg dut_sdo_driven;
	reg dut_sdo_value;
	reg dut_rst_driven;
	reg dut_rst_value;
	`define DUT_SDO		33
	reg [10:0] sdi_buf;
	reg [10:0] sii_buf;
	reg [10:0] sdo_buf;

	wire low, high;		/* Constant lo/hi */
	assign low = 0;
	assign high = 1;

	initial begin
		prog_busy <= 0;
		prog_command <= 0;
		prog_state <= 0;
		prog_count <= 0;
		dut_sdi <= 0;
		dut_sii <= 0;
		dut_sci_manual <= 0;
		dut_sci_auto <= 0;
		dut_sdo_driven <= 0;
		dut_sdo_value <= 0;
		dut_rst_driven <= 0;
		dut_rst_value <= 0;
		sdi_buf <= 0;
		sii_buf <= 0;
		sdo_buf <= 0;
	end

	/* The delay counter. Based on the 12MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	always @(posedge osc) begin
		if (delay_count == 0 && prog_busy[0] != prog_busy[1]) begin
			case (prog_command)
			`CMD_SENDINSTR: begin
				case (prog_state)
				0: begin
					dut_sdi <= sdi_buf[10 - prog_count];
					dut_sii <= sii_buf[10 - prog_count];
					prog_state <= 1;
					delay_count <= 3 - 1;	/* 100ns */
				end
				1: begin
					dut_sci_auto <= 1;	/* CLK hi */
					prog_state <= 2;
					delay_count <= 3 - 1;	/* 100ns */
				end
				2: begin
					sdo_buf[10 - prog_count] <= zif[`DUT_SDO];
					prog_count <= prog_count + 1;
					prog_state <= 3;
					delay_count <= 3 - 1;	/* 100ns */
				end
				3: begin
					dut_sci_auto <= 0;	/* CLK lo */
					delay_count <= 4 - 1;	/* 150ns */
					if (prog_count == 11) begin
						prog_state <= 0;
						prog_count <= 0;
						prog_busy[1] <= prog_busy[0]; /* done */
					end else begin
						prog_state <= 0;
					end
				end
				endcase
			end
			endcase
		end else begin
			delay_count <= delay_count - 1;
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin /* Unused */
		end
		8'h12: begin /* Run command */
			prog_command <= data;
			prog_busy[0] <= ~prog_busy[1];
		end
		8'h13: begin /* Load SDI sequence */
			sdi_buf[1:0] <= 0;
			sdi_buf[9:2] <= data;
			sdi_buf[10] <= 0;
		end
		8'h14: begin /* Load SII sequence */
			sii_buf[1:0] <= 0;
			sii_buf[9:2] <= data;
			sii_buf[10] <= 0;
		end
		8'h15: begin /* Set signals manually */
			dut_sci_manual <= data[0];	/* SCI */
			dut_sdo_driven <= data[1];	/* SDO drive-enable */
			dut_sdo_value <= data[2];	/* SDO drive-value */
			dut_rst_driven <= data[3];	/* RESET drive-enable */
			dut_rst_value <= data[4];	/* RESET drive-value */
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin /* Unused */
		end
		8'h12: begin /* Read status */
			read_data[0] <= (prog_busy[0] != prog_busy[1]);	/* busy */
			read_data[1] <= zif[`DUT_SDO];			/* Raw SDO pin access */
		end
		8'h13: begin /* Get SDO sequence (low) */
			read_data[7:0] <= sdo_buf[7:0];
		end
		8'h14: begin /* Get SDO sequence (high) */
			read_data[2:0] <= sdo_buf[10:8];
		end
		endcase
	end

	always @(negedge ale) begin
		address <= data;
	end

	assign dut_sci = (prog_busy[0] == prog_busy[1]) ? dut_sci_manual : dut_sci_auto;
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
	bufif0(zif[15], dut_rst_value, !dut_rst_driven);	/* RESET */
	bufif0(zif[16], dut_sci, low);				/* SCI */
	bufif0(zif[17], low, high);				/* PB4 */
	bufif0(zif[18], low, low);				/* GND */
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
	bufif0(zif[31], dut_sdi, low);				/* SDI */
	bufif0(zif[32], dut_sii, low);				/* SII */
	bufif0(zif[33], dut_sdo_value, !dut_sdo_driven);	/* SDO */
	bufif0(zif[34], high, low);				/* VCC */
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
