/*
 *   TOP2049 Open Source programming suite
 *
 *   Winbond W29EE011 DIP32
 *   FPGA bottomhalf implementation
 *
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
`define RUNTIME_ID	16'h0009
`define RUNTIME_REV	16'h01

module w29ee011dip32(data, ale, write, read, osc_in, zif);
	inout [7:0] data;
	input ale;
	input write;
	input read;
	input osc_in; /* 24MHz oscillator */
	inout [48:1] zif;

	/* Interface to the microcontroller */
	wire read_oe;			/* Read output-enable */
	reg [7:0] address;		/* Cached address value */
	reg [7:0] read_data;		/* Cached read data */

	wire low, high;		/* Constant lo/hi */
	assign low = 0;
	assign high = 1;

	/* Programmer context */
	reg [1:0] prog_busy;
	reg [3:0] prog_command;
	reg [3:0] prog_state;
	reg [16:0] prog_addr;
	parameter WRITE_BUF_SIZE = 128;
	reg [7:0] write_buf[0:WRITE_BUF_SIZE-1];
	//synthesis attribute ram_style write_buf block;
	reg [7:0] write_buf_count;
	reg [7:0] write_buf_iter;
	parameter JEDEC_BUF_SIZE = 6;
	reg [7:0] jedec_addr_lo[0:JEDEC_BUF_SIZE-1];
	reg [7:0] jedec_addr_med[0:JEDEC_BUF_SIZE-1];
	reg [0:0] jedec_addr_hi[0:JEDEC_BUF_SIZE-1];
	reg [7:0] jedec_data[0:JEDEC_BUF_SIZE-1];
	reg [2:0] jedec_buf_count;
	reg [2:0] jedec_buf_iter;
	reg in_jedec;
	reg [16:0] dut_write_addr;
	reg [16:0] dut_read_addr;
	wire [16:0] dut_addr;
	reg [7:0] dut_jedec_data;
	reg [7:0] dut_write_data;
	wire [7:0] dut_data;
	reg dut_ce;
	reg dut_oe;
	reg dut_we;

	/* Programmer commands */
	parameter CMD_WRITEBUF		= 1;

	/* The delay counter. Based on the 24MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	initial begin
		address <= 0;
		read_data <= 0;
		delay_count <= 0;

		prog_busy <= 0;
		prog_command <= 0;
		prog_state <= 0;
		prog_addr <= 0;
		write_buf_count <= 0;
		write_buf_iter <= 0;
		jedec_buf_count <= 0;
		jedec_buf_iter <= 0;
		in_jedec <= 1;
		dut_write_addr <= 0;
		dut_read_addr <= 0;
		dut_jedec_data <= 0;
		dut_write_data <= 0;
		dut_ce <= 1;
		dut_oe <= 1;
		dut_we <= 1;
	end

	`define DELAY_1US	delay_count <= (24 * 1) - 1
	`define DELAY_350US	delay_count <= (24 * 350) - 1

	always @(posedge osc) begin
		if (delay_count == 0) begin
			if (prog_busy[0] != prog_busy[1]) begin
				case (prog_command)
				CMD_WRITEBUF: begin
					case (prog_state)
					0: begin
						in_jedec <= 1;
						dut_write_addr[7:0] <= jedec_addr_lo[jedec_buf_iter];
						dut_write_addr[15:8] <= jedec_addr_med[jedec_buf_iter];
						dut_write_addr[16] <= jedec_addr_hi[jedec_buf_iter];
						dut_jedec_data <= jedec_data[jedec_buf_iter];
						dut_we <= 0;
						jedec_buf_iter <= jedec_buf_iter + 1;
						prog_state <= 1;
						`DELAY_1US;
					end
					1: begin
						dut_we <= 1;
						if (jedec_buf_iter == jedec_buf_count)
							prog_state <= 2; /* Advance to payload */
						else
							prog_state <= 0;
						`DELAY_1US;
					end
					2: begin
						if (write_buf_count == 0) begin
							/* Done. No payload. */
							prog_state <= 5;
							`DELAY_350US;
						end else begin
							prog_state <= 3;
							in_jedec <= 0;
							dut_write_addr <= prog_addr;
						end
					end
					3: begin
						dut_write_data <= write_buf[write_buf_iter];
						dut_we <= 0;
						write_buf_iter <= write_buf_iter + 1;
						prog_state <= 4;
						`DELAY_1US;
					end
					4: begin
						dut_we <= 1;
						if (write_buf_iter == write_buf_count) begin
							prog_state <= 5;
							`DELAY_350US;
						end else begin
							dut_write_addr <= dut_write_addr + 1;
							prog_state <= 3;
							`DELAY_1US;
						end
					end
					5: begin
						/* Done. The final delay for the actual operation to
						 * finish is done in software. */
						jedec_buf_iter <= 0;
						write_buf_iter <= 0;
						prog_state <= 0;
						prog_busy[1] <= prog_busy[0];
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
		8'h10: begin /* Write to temporary write-buffer */
			write_buf[write_buf_count] <= data;
			write_buf_count <= write_buf_count + 1;
		end
		8'h12: begin /* Run command */
			prog_command <= data;
			prog_busy[0] <= ~prog_busy[1];
		end
		8'h13: begin /* Reset temporary write-buffer count */
			jedec_buf_count <= 0;
			write_buf_count <= 0;
		end
		8'h14: begin /* Write start address low */
			prog_addr[7:0] <= data;
		end
		8'h15: begin /* Write start address med */
			prog_addr[15:8] <= data;
		end
		8'h16: begin /* Write start address high */
			prog_addr[16] <= data[0];
		end
		8'h17: begin /* Read address low */
			dut_read_addr[7:0] <= data;
		end
		8'h18: begin /* Read address med */
			dut_read_addr[15:8] <= data;
		end
		8'h19: begin /* Read address high */
			dut_read_addr[16] <= data[0];
		end
		8'h1A: begin /* Set #CE, #OE */
			dut_ce <= data[0];
			dut_oe <= data[1];
		end
		8'h1B: begin /* JEDEC command buffer write addr lo */
			jedec_addr_lo[jedec_buf_count] <= data;
		end
		8'h1C: begin /* JEDEC command buffer write addr med */
			jedec_addr_med[jedec_buf_count] <= data;
		end
		8'h1D: begin /* JEDEC command buffer write addr hi */
			jedec_addr_hi[jedec_buf_count] <= data[0];
		end
		8'h1E: begin /* JEDEC command buffer write data */
			jedec_data[jedec_buf_count] <= data;
			jedec_buf_count <= jedec_buf_count + 1;
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin /* Data read */
			read_data[2:0] <= zif[23:21];
			read_data[7:3] <= zif[29:25];
		end
		8'h12: begin /* Status read */
			read_data[0] <= (prog_busy[0] != prog_busy[1]);
		end

		8'hFD: read_data <= `RUNTIME_ID & 16'hFF;
		8'hFE: read_data <= (`RUNTIME_ID >> 8) & 16'hFF;
		8'hFF: read_data <= `RUNTIME_REV;
		endcase
	end

	always @(negedge ale) begin
		address <= data;
	end

	assign dut_addr = (prog_busy[0] == prog_busy[1]) ? dut_read_addr : dut_write_addr;
	assign dut_data = in_jedec ? dut_jedec_data : dut_write_data;
	assign read_oe = !read && address[4];

	bufif0(zif[1], low, low);
	bufif0(zif[2], low, low);
	bufif0(zif[3], low, low);
	bufif0(zif[4], low, low);
	bufif0(zif[5], low, low);
	bufif0(zif[6], low, low);
	bufif0(zif[7], low, low);
	bufif0(zif[8], low, low);
	bufif0(zif[9], low, high);		/* NC */
	bufif0(zif[10], dut_addr[16], low);	/* A16 */
	bufif0(zif[11], dut_addr[15], low);	/* A15 */
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
	bufif0(zif[30], dut_ce, low);		/* #CE */
	bufif0(zif[31], dut_addr[10], low);	/* A10 */
	bufif0(zif[32], dut_oe, low);		/* #OE */
	bufif0(zif[33], dut_addr[11], low);	/* A11 */
	bufif0(zif[34], dut_addr[9], low);	/* A9 */
	bufif0(zif[35], dut_addr[8], low);	/* A8 */
	bufif0(zif[36], dut_addr[13], low);	/* A13 */
	bufif0(zif[37], dut_addr[14], low);	/* A14 */
	bufif0(zif[38], low, high);		/* NC */
	bufif0(zif[39], dut_we, low);		/* #WE */
	bufif0(zif[40], high, low);		/* VDD */
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
