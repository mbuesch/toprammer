/*
 *   TOP2049 Open Source programming suite
 *
 *   M24C16 I2C based serial EEPROM
 *   FPGA bottomhalf implementation
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

/* The runtime ID and revision. */
`define RUNTIME_ID	16'h000B
`define RUNTIME_REV	16'h01

module i2c_module(clock, nreset,
		  scl, sda_out, sda_out_en, sda_in,
		  write_byte, read_byte, read_mode,
		  do_start, expect_ack, do_stop,
		  finished);
	input clock;
	input nreset;
	output scl;
	output sda_out;
	output sda_out_en;
	input sda_in;
	input [7:0] write_byte;
	output [7:0] read_byte;
	input read_mode;
	input do_start;
	input expect_ack;
	input do_stop;
	output finished;

	reg [0:0] start_state;
	reg [1:0] data_state;
	reg [0:0] ack_state;
	reg [0:0] stop_state;
	reg [2:0] bit_index;

	reg sda_out_reg;
	reg sda_out_en_reg;
	reg [1:0] scl_reg;
	reg scl_running;
	reg [7:0] read_byte_reg;
	reg finished_reg;

	wire [1:0] scl_pos;
	assign scl_pos = scl_reg + 1;
	parameter SCL_HILO	= 0;
	parameter SCL_LO	= 1;
	parameter SCL_LOHI	= 2;
	parameter SCL_HI	= 3;

	assign sda_out = sda_out_reg;
	assign sda_out_en = sda_out_en_reg;
	assign scl = scl_reg[1];
	assign read_byte = read_byte_reg;
	assign finished = finished_reg;

	initial begin
		start_state <= 0;
		data_state <= 0;
		ack_state <= 0;
		stop_state <= 0;
		bit_index <= 7;

		sda_out_reg <= 1;
		sda_out_en_reg <= 0;
		scl_reg <= SCL_HI;
		scl_running <= 0;
		read_byte_reg <= 0;
		finished_reg <= 0;
	end

	always @(posedge clock or negedge nreset) begin
		if (nreset == 0) begin
			/* Reset */
			start_state <= 0;
			data_state <= 0;
			ack_state <= 0;
			stop_state <= 0;

			bit_index <= 7;

			sda_out_reg <= 1;
			sda_out_en_reg <= 0;
			scl_reg <= SCL_HI;
			scl_running <= 0;
			read_byte_reg <= 0;

			finished_reg <= 0;
		end else begin

			if (scl_running) begin
				scl_reg <= scl_reg + 1;
			end else begin
				scl_reg <= SCL_HI;
			end

			if (do_start && start_state != 1) begin
				/* Send start condition */
				finished_reg <= 0;
				scl_running <= 1;
				sda_out_en_reg <= 1;
				case (start_state)
				0: begin
					/* Start condition latch */
					if (scl_pos == SCL_HI) begin
						sda_out_reg <= 0;
						start_state <= 1;
					end
				end
				endcase
			end else if (data_state != 3) begin
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
							sda_out_reg <= write_byte[bit_index];
						end
						if (bit_index == 0) begin
							data_state <= 2;
						end else begin
							data_state <= 1;
						end
					end
				end
				1: begin
					if (scl_pos == SCL_LOHI) begin
						bit_index <= bit_index - 1;
					end else if (scl_pos == SCL_HI) begin
						if (read_mode) begin
							read_byte_reg[bit_index + 1] <= sda_in;
						end
						data_state <= 0;
					end
				end
				2: begin
					if (scl_pos == SCL_LOHI) begin
						bit_index <= 7;
					end else if (scl_pos == SCL_HI) begin
						if (read_mode) begin
							read_byte_reg[0] <= sda_in;
						end
						data_state <= 3;
					end
				end
				endcase
			end else if (expect_ack && ack_state != 1) begin
				/* Wait for ACK from chip */
				finished_reg <= 0;
				scl_running <= 1;
				case (ack_state)
				0: begin
					if (scl_pos == SCL_LO) begin
						sda_out_en_reg <= 0;
					end else if (scl_pos == SCL_HI) begin
						if (sda_in == 0) begin
							/* Got it */
							ack_state <= 1;
						end
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
						scl_running <= 0;
						stop_state <= 1;
					end
				end
				endcase
			end else begin
				finished_reg <= 1;
			end
		end
	end
endmodule

module m24c16dip8(data, ale_in, write, read, osc_in, zif);
	inout [7:0] data;
	input ale_in;
	input write;
	input read;
	input osc_in; /* 24MHz oscillator */
	inout [48:1] zif;

	/* Interface to the microcontroller */
	wire read_oe;		/* Read output-enable */
	reg [7:0] address;	/* Cached address value */
	reg [7:0] read_data;	/* Cached read data */

	/* Programmer API and statemachine */
	reg [1:0] cmd_busy;	/* bit0 != bit1 >= busy */
	reg [3:0] command;
	reg [7:0] data_buffer;

	`define IS_BUSY		(cmd_busy[0] != cmd_busy[1])	/* Is running command? */
	`define SET_FINISHED	cmd_busy[1] <= cmd_busy[0]	/* Set command-finished */

	/* Programmer commands */
	parameter CMD_DEVSEL_READ	= 0;
	parameter CMD_DEVSEL_WRITE	= 1;
	parameter CMD_SETADDR		= 2;
	parameter CMD_DATA_READ		= 3;
	parameter CMD_DATA_READ_STOP	= 4;
	parameter CMD_DATA_WRITE	= 5;
	parameter CMD_DATA_WRITE_STOP	= 6;

	/* Chip signals */
	reg chip_e0;		/* E0 */
	reg chip_e0_en;		/* E0 enable */
	reg chip_e1;		/* E1 */
	reg chip_e1_en;		/* E1 enable */
	reg chip_e2;		/* E2 */
	reg chip_e2_en;		/* E2 enable */
	reg chip_wc;		/* /WC */
	wire chip_scl;		/* I2C SCL */
	wire chip_sda_out;	/* I2C SDA out */
	wire chip_sda_out_en;	/* I2C SDA out enable */
	parameter ZIF_SDA	= 25;

	wire low, high;		/* Constant lo/hi */
	assign low = 0;
	assign high = 1;

	/* I2C interface */
	reg i2c_clock;
	reg i2c_nreset;
	reg [7:0] i2c_write_byte;
	wire [7:0] i2c_read_byte;
	reg i2c_read;			/* 1=> Read mode */
	reg i2c_do_start;
	reg i2c_expect_ack;
	reg i2c_do_stop;
	wire i2c_finished;
	reg [1:0] i2c_running;

	i2c_module i2c(
		.clock(i2c_clock),
		.nreset(i2c_nreset),
		.scl(chip_scl),
		.sda_out(chip_sda_out),
		.sda_out_en(chip_sda_out_en),
		.sda_in(zif[ZIF_SDA]),
		.write_byte(i2c_write_byte),
		.read_byte(i2c_read_byte),
		.read_mode(i2c_read),
		.do_start(i2c_do_start),
		.expect_ack(i2c_expect_ack),
		.do_stop(i2c_do_stop),
		.finished(i2c_finished)
	);

	/* The delay counter. Based on the 24MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	`define DELAY_1P5US	delay_count <= 36 - 1	/* 1.5 microseconds */

	initial begin
		address <= 0;
		read_data <= 0;
		delay_count <= 0;

		cmd_busy <= 0;
		command <= 0;
		data_buffer <= 0;

		chip_e0 <= 0;
		chip_e0_en <= 0;
		chip_e1 <= 0;
		chip_e1_en <= 0;
		chip_e2 <= 0;
		chip_e2_en <= 0;
		chip_wc <= 0;

		i2c_clock <= 0;
		i2c_nreset <= 0;
		i2c_write_byte <= 0;
		i2c_read <= 0;
		i2c_do_start <= 0;
		i2c_expect_ack <= 0;
		i2c_do_stop <= 0;
		i2c_running <= 0;
	end

	always @(posedge osc) begin
		if (delay_count == 0 && `IS_BUSY) begin
			if (i2c_running) begin
				if (i2c_finished && i2c_running == 2) begin
					i2c_running <= 0;
					i2c_nreset <= 0;
					`SET_FINISHED;
				end else begin
					i2c_running <= 2;
					i2c_clock <= ~i2c_clock;
					delay_count <= 1000;
//					`DELAY_1P5US;
				end
			end else begin
				i2c_nreset <= 1;
/*
					i2c_write_byte[7] <= 1;
					i2c_write_byte[6] <= 0;
					i2c_write_byte[5] <= 1;
					i2c_write_byte[4] <= 0;
					i2c_write_byte[3] <= 1;
					i2c_write_byte[2] <= 0;
					i2c_write_byte[1] <= 1;
					i2c_write_byte[0] <= 0;
					i2c_clock <= 0;
					i2c_read <= 0;
					i2c_do_start <= 1;
					i2c_expect_ack <= 0;
					i2c_do_stop <= 1;
					i2c_running <= 1;
*/
				case (command)
				CMD_DEVSEL_READ: begin
					i2c_write_byte[7] <= 1;
					i2c_write_byte[6] <= 0;
					i2c_write_byte[5] <= 1;
					i2c_write_byte[4] <= 0;
					i2c_write_byte[3] <= chip_e2;
					i2c_write_byte[2] <= chip_e1;
					i2c_write_byte[1] <= chip_e0;
					i2c_write_byte[0] <= 1; /* Read */
					i2c_clock <= 0;
					i2c_read <= 0;
					i2c_do_start <= 1;
					i2c_expect_ack <= 1;
					i2c_do_stop <= 0;
					i2c_running <= 1;
				end
				CMD_DEVSEL_WRITE: begin
					i2c_write_byte[7] <= 1;
					i2c_write_byte[6] <= 0;
					i2c_write_byte[5] <= 1;
					i2c_write_byte[4] <= 0;
					i2c_write_byte[3] <= chip_e2;
					i2c_write_byte[2] <= chip_e1;
					i2c_write_byte[1] <= chip_e0;
					i2c_write_byte[0] <= 0; /* Write */
					i2c_clock <= 0;
					i2c_read <= 0;
					i2c_do_start <= 1;
					i2c_expect_ack <= 1;
					i2c_do_stop <= 0;
					i2c_running <= 1;
				end
				CMD_SETADDR: begin
					i2c_write_byte <= data_buffer;
					i2c_clock <= 0;
					i2c_read <= 0;
					i2c_do_start <= 0;
					i2c_expect_ack <= 1;
					i2c_do_stop <= 0;
					i2c_running <= 1;
				end
				CMD_DATA_READ: begin
					i2c_clock <= 0;
					i2c_read <= 1;
					i2c_do_start <= 0;
					i2c_expect_ack <= 1;
					i2c_do_stop <= 0;
					i2c_running <= 1;
				end
				CMD_DATA_READ_STOP: begin
					i2c_clock <= 0;
					i2c_read <= 1;
					i2c_do_start <= 0;
					i2c_expect_ack <= 0;
					i2c_do_stop <= 1;
					i2c_running <= 1;
				end
				CMD_DATA_WRITE: begin
					i2c_write_byte <= data_buffer;
					i2c_clock <= 0;
					i2c_read <= 0;
					i2c_do_start <= 0;
					i2c_expect_ack <= 1;
					i2c_do_stop <= 0;
					i2c_running <= 1;
				end
				CMD_DATA_WRITE_STOP: begin
					i2c_write_byte <= data_buffer;
					i2c_clock <= 0;
					i2c_read <= 0;
					i2c_do_start <= 0;
					i2c_expect_ack <= 1;
					i2c_do_stop <= 1;
					i2c_running <= 1;
				end
				endcase
			end
		end else begin
			if (delay_count != 0) begin
				delay_count <= delay_count - 1;
			end
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin /* Run command */
			command <= data;
			cmd_busy[0] <= ~cmd_busy[1];
		end
		8'h11: begin /* Write to data buffer */
			data_buffer[7:0] <= data[7:0];
		end
		8'h12: begin /* Set control pins */
			chip_e0 <= data[0];
			chip_e0_en <= data[1];
			chip_e1 <= data[2];
			chip_e1_en <= data[3];
			chip_e2 <= data[4];
			chip_e2_en <= data[5];
			chip_wc <= data[6];
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin /* Read data buffer */
			read_data <= i2c_read_byte;
		end
		8'h11: begin /* Status read */
			read_data[0] <= cmd_busy[0];
			read_data[1] <= cmd_busy[1];
		end

		8'hFD: read_data <= `RUNTIME_ID & 16'hFF;
		8'hFE: read_data <= (`RUNTIME_ID >> 8) & 16'hFF;
		8'hFF: read_data <= `RUNTIME_REV;
		endcase
	end

	wire ale;
	IBUFG ale_ibufg(.I(ale_in), .O(ale));

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
	bufif0(zif[21], chip_e0, !chip_e0_en);			/* E0 */
	bufif0(zif[22], chip_e1, !chip_e1_en);			/* E1 */
	bufif0(zif[23], chip_e2, !chip_e2_en);			/* E2 */
	bufif0(zif[24], low, low);				/* VSS */
	bufif0(zif[25], chip_sda_out, !chip_sda_out_en);	/* SDA */
	bufif0(zif[26], chip_scl, low);				/* SCL */
	bufif0(zif[27], chip_wc, low);				/* /WC */
	bufif0(zif[28], high, low);				/* VCC */
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
