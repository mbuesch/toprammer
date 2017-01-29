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

`include "common.vh"
`include "i2c.v"

`BOTTOMHALF_BEGIN(m24c16dip8, 11, 1)
	reg [7:0] data_buffer;

	/* Chip signals */
	reg chip_e0;		/* E0 */
	reg chip_e0_en;		/* E0 enable */
	reg chip_e1;		/* E1 */
	reg chip_e1_en;		/* E1 enable */
	reg chip_e2;		/* E2 */
	reg chip_e2_en;		/* E2 enable */
	reg chip_wc;		/* /WC */
	wire chip_scl_out;	/* I2C SCL out */
	wire chip_scl_out_en;	/* I2C SCL out enable*/
	wire chip_sda_out;	/* I2C SDA out */
	wire chip_sda_out_en;	/* I2C SDA out enable */
	parameter ZIF_SDA	= 25;
	parameter ZIF_SCL	= 26;

	/* I2C interface */
	reg i2c_clock;
	reg i2c_nreset;
	reg [7:0] i2c_write_byte;
	wire [7:0] i2c_read_byte;
	reg i2c_read;			/* 1=> Read mode */
	wire i2c_ack;
	reg i2c_drive_ack;
	reg i2c_do_start;
	reg i2c_do_stop;
	wire i2c_finished;
	reg i2c_running;

	i2c_module i2c(
		.clock(i2c_clock),
		.nreset(i2c_nreset),
		.scl_out(chip_scl_out),
		.scl_out_en(chip_scl_out_en),
		.scl_in(zif[ZIF_SCL]),
		.sda_out(chip_sda_out),
		.sda_out_en(chip_sda_out_en),
		.sda_in(zif[ZIF_SDA]),
		.write_byte(i2c_write_byte),
		.read_byte(i2c_read_byte),
		.read_mode(i2c_read),
		.ack(i2c_ack),
		.drive_ack(i2c_drive_ack),
		.do_start(i2c_do_start),
		.do_stop(i2c_do_stop),
		.finished(i2c_finished)
	);

	`INITIAL_BEGIN
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
		i2c_drive_ack <= 0;
		i2c_do_start <= 0;
		i2c_do_stop <= 0;
		i2c_running <= 0;
	`INITIAL_END

	`ASYNCPROC_BEGIN
		if (`CMD_IS_RUNNING) begin
			if (i2c_running) begin
				if (i2c_finished && i2c_clock) begin
					i2c_running <= 0;
					`CMD_FINISH
				end else begin
					i2c_clock <= ~i2c_clock;
					`UDELAY(250)
				end
			end else begin
				i2c_write_byte	<= data_buffer;
				i2c_read	<= `CMD_NR[0];
				i2c_do_start	<= `CMD_NR[1];
				i2c_do_stop	<= `CMD_NR[2];
				i2c_drive_ack	<= `CMD_NR[3];
				i2c_clock	<= 0;
				i2c_running	<= 1;
				i2c_nreset	<= 1;
			end
		end
	`ASYNCPROC_END

	`DATAWRITE_BEGIN
		`ADDR(0): begin /* Run command */
			`CMD_RUN(in_data)
		end
		`ADDR(1): begin /* Write to data buffer */
			data_buffer[7:0] <= in_data[7:0];
		end
		`ADDR(2): begin /* Set control pins */
			chip_e0 <= in_data[0];
			chip_e0_en <= in_data[1];
			chip_e1 <= in_data[2];
			chip_e1_en <= in_data[3];
			chip_e2 <= in_data[4];
			chip_e2_en <= in_data[5];
			chip_wc <= in_data[6];
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin /* Read data buffer */
			out_data <= i2c_read_byte;
		end
		`ADDR(1): begin /* Status read */
			out_data[0] <= `CMD_IS_RUNNING;
			out_data[1] <= i2c_ack;
		end
	`DATAREAD_END

	`ZIF_UNUSED(1) `ZIF_UNUSED(2) `ZIF_UNUSED(3) `ZIF_UNUSED(4)
	`ZIF_UNUSED(5) `ZIF_UNUSED(6) `ZIF_UNUSED(7) `ZIF_UNUSED(8)
	`ZIF_UNUSED(9) `ZIF_UNUSED(10) `ZIF_UNUSED(11) `ZIF_UNUSED(12)
	`ZIF_UNUSED(13) `ZIF_UNUSED(14) `ZIF_UNUSED(15) `ZIF_UNUSED(16)
	`ZIF_UNUSED(17) `ZIF_UNUSED(18) `ZIF_UNUSED(19) `ZIF_UNUSED(20)
	`ZIF_BUF1(21, chip_e0, chip_e0_en)		/* E0 */
	`ZIF_BUF1(22, chip_e1, chip_e1_en)		/* E1 */
	`ZIF_BUF1(23, chip_e2, chip_e2_en)		/* E2 */
	`ZIF_BUF1(24, low, high)			/* VSS */
	`ZIF_BUF1(25, chip_sda_out, chip_sda_out_en)	/* SDA */
	`ZIF_BUF1(26, chip_scl_out, chip_scl_out_en)	/* SCL */
	`ZIF_BUF1(27, chip_wc, high)			/* /WC */
	`ZIF_BUF1(28, high, high)			/* VCC */
	`ZIF_UNUSED(29) `ZIF_UNUSED(30) `ZIF_UNUSED(31) `ZIF_UNUSED(32)
	`ZIF_UNUSED(33) `ZIF_UNUSED(34) `ZIF_UNUSED(35) `ZIF_UNUSED(36)
	`ZIF_UNUSED(37) `ZIF_UNUSED(38) `ZIF_UNUSED(39) `ZIF_UNUSED(40)
	`ZIF_UNUSED(41) `ZIF_UNUSED(42) `ZIF_UNUSED(43) `ZIF_UNUSED(44)
	`ZIF_UNUSED(45) `ZIF_UNUSED(46) `ZIF_UNUSED(47) `ZIF_UNUSED(48)
`BOTTOMHALF_END
