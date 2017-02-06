/*
 *   TOP2049 Open Source programming suite
 *
 *   FPGA bottomhalf I2C bus implementation
 *
 *   Copyright (c) 2011-2017 Michael Buesch <m@bues.ch>
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

module i2c_module(clock, nreset,
		  scl_out, scl_out_en, scl_in,
		  sda_out, sda_out_en, sda_in,
		  write_byte, read_byte, read_mode,
		  ack, drive_ack,
		  do_start, do_stop,
		  finished);
	input clock;
	input nreset;
	output scl_out;
	output scl_out_en;
	input scl_in;
	output sda_out;
	output sda_out_en;
	input sda_in;
	input [7:0] write_byte;
	output [7:0] read_byte;
	input read_mode;
	output ack;
	input drive_ack;
	input do_start;
	input do_stop;
	output finished;

	reg [1:0] start_state;
	reg [1:0] data_state;
	reg [0:0] ack_state;
	reg [0:0] stop_state;
	reg [3:0] bit_index;

	reg sda_out_reg;
	reg sda_out_en_reg;
	reg [1:0] scl_out_reg;
	reg scl_out_en_reg;
	reg scl_running;
	reg [7:0] read_byte_reg;
	reg ack_reg;
	reg finished_reg;

	wire [1:0] scl_pos;
	assign scl_pos = (scl_out_reg + 1) & 3;
	parameter SCL_HILO	= 0;
	parameter SCL_LO	= 1;
	parameter SCL_LOHI	= 2;
	parameter SCL_HI	= 3;

	wire [7:0] write_byte_wire;
	assign write_byte_wire[0] = write_byte[7];
	assign write_byte_wire[1] = write_byte[6];
	assign write_byte_wire[2] = write_byte[5];
	assign write_byte_wire[3] = write_byte[4];
	assign write_byte_wire[4] = write_byte[3];
	assign write_byte_wire[5] = write_byte[2];
	assign write_byte_wire[6] = write_byte[1];
	assign write_byte_wire[7] = write_byte[0];
	assign read_byte[0] = read_byte_reg[7];
	assign read_byte[1] = read_byte_reg[6];
	assign read_byte[2] = read_byte_reg[5];
	assign read_byte[3] = read_byte_reg[4];
	assign read_byte[4] = read_byte_reg[3];
	assign read_byte[5] = read_byte_reg[2];
	assign read_byte[6] = read_byte_reg[1];
	assign read_byte[7] = read_byte_reg[0];
	assign sda_out = sda_out_reg;
	assign sda_out_en = sda_out_en_reg;
	assign scl_out = scl_out_reg[1];
	assign scl_out_en = scl_out_en_reg;
	assign ack = ack_reg;
	assign finished = finished_reg;

	initial begin
		start_state <= 0;
		data_state <= 0;
		ack_state <= 0;
		stop_state <= 0;
		bit_index <= 0;

		sda_out_reg <= 1;
		sda_out_en_reg <= 0;
		scl_out_reg <= SCL_HI;
		scl_out_en_reg <= 1;
		scl_running <= 0;
		read_byte_reg <= 0;
		ack_reg <= 0;
		finished_reg <= 0;
	end

//TODO clock stretching

	always @(posedge clock or negedge nreset) begin
		if (nreset == 0) begin
			/* Reset */
			start_state <= 0;
			data_state <= 0;
			ack_state <= 0;
			stop_state <= 0;

			bit_index <= 0;

			sda_out_reg <= 1;
			sda_out_en_reg <= 0;
			scl_out_reg <= SCL_HI;
			scl_out_en_reg <= 1;
			scl_running <= 0;
			read_byte_reg <= 0;
			ack_reg <= 0;

			finished_reg <= 0;
		end else begin

//			if (scl_running) begin
				scl_out_reg <= scl_out_reg + 1;
//			end else begin
//				scl_out_reg <= SCL_HI;
//			end

			if (do_start && start_state != 2) begin
				/* Send start condition */
				finished_reg <= 0;
				scl_running <= 1;
				sda_out_en_reg <= 1;
				case (start_state)
				0: begin
					/* Begin with SDA=hi */
					sda_out_reg <= 1;
					if (scl_pos == SCL_LOHI) begin
						start_state <= 1;
					end
				end
				1: begin
					/* Start condition latch */
					if (scl_pos == SCL_HI) begin
						sda_out_reg <= 0;
						start_state <= 2;
					end
				end
				endcase
			end else if (data_state != 2) begin
				/* Data transfer */
				finished_reg <= 0;
				scl_running <= 1;
				sda_out_en_reg <= !read_mode;
				case (data_state)
				0: begin
					if (scl_pos == SCL_LO) begin
						if (read_mode) begin
							sda_out_reg <= 0;
						end else begin
							sda_out_reg <= write_byte_wire[bit_index & 7];
						end
						data_state <= 1;
					end
				end
				1: begin
					if (scl_pos == SCL_HI) begin
						bit_index <= bit_index + 1;
						if (read_mode) begin
							read_byte_reg[bit_index & 7] <= sda_in;
						end
						if (bit_index >= 7) begin
							data_state <= 2;
						end else begin
							data_state <= 0;
						end
					end
				end
				endcase
			end else if (ack_state != 1) begin
				/* Read ACK bit */
				finished_reg <= 0;
				scl_running <= 1;
				case (ack_state)
				0: begin
					if (scl_pos == SCL_LO) begin
						sda_out_en_reg <= drive_ack;
						sda_out_reg <= 0;
					end else if (scl_pos == SCL_HI) begin
						ack_reg <= sda_in;
						ack_state <= 1;
					end
				end
				endcase
			end else if (do_stop && stop_state != 1) begin
				/* Send stop condition */
				finished_reg <= 0;
				sda_out_en_reg <= 1;
				case (stop_state)
				0: begin
					if (scl_pos == SCL_HI) begin
						sda_out_reg <= 1;
						stop_state <= 1;
					end
				end
				endcase
			end else begin
				if (scl_pos == SCL_HILO) begin
					start_state <= 0;
					data_state <= 0;
					ack_state <= 0;
					stop_state <= 0;

					bit_index <= 0;

					finished_reg <= 1;
//					scl_running <= 0;
				end else begin
					finished_reg <= 0;
				end
			end
		end
	end
endmodule
