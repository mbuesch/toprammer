/*
 *   TOP2049 Open Source programming suite
 *
 *   Microchip PIC10f200 DIP10 (DIP8, but needs a shift due to GND and Vcc pin placement)
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2012 Pavel Stemberk <stemberk@gmail.com>
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

`define DELAY42NSEC(D42NSEC)	__delay_count <= (D42NSEC) - 1;//41.666 ns wait cycle if D42NSEC = 1

`BOTTOMHALF_BEGIN(pic10fXXXdip8, 13, 1)
	/* Programmer context */
	reg [7:0] prog_count;
	`define CMD_SENDINSTR	1
	`define CMD_SENDDATA	2
	`define CMD_READDATA	3
	reg dut_sci_manual;
	reg dut_sci_auto;
	wire dut_sci;
	reg dut_sdio_driven;
	reg dut_sdio_value;
	reg dut_vpp;
	`define DUT_SDIO	27
	reg [15:0] sdi_buf;
	reg [15:0] sdo_buf;

	initial begin
		prog_count <= 0;
		dut_sci_manual <= 0;
		dut_sci_auto <= 0;
		dut_sdio_driven <= 0;
		dut_sdio_value <= 0;
		sdi_buf <= 0;
		sdo_buf <= 0;
		dut_vpp <= 0;
	end

	`ASYNCPROC_BEGIN
		if (`CMD_IS_RUNNING) begin
			case (`CMD_STATE)
			0: begin
				if (`CMD_IS(`CMD_SENDINSTR) ||
				    `CMD_IS(`CMD_SENDDATA)) begin
					dut_sdio_driven <= 1;
				end else begin
					dut_sdio_driven <= 0;
				end
				//dut_vpp <= 1;
				`CMD_STATE_SET(1)
				`DELAY42NSEC(5)
			end
			1: begin
				dut_sci_auto <= 1;  /* CLK hi */
				/* 80ns after this moment we need to be 
				 * prepared in CMD_READDATA case */
				case(`CMD_NR)
				`CMD_SENDDATA: begin
					dut_sdio_value <= sdi_buf[prog_count];
				end
				`CMD_SENDINSTR: begin
					dut_sdio_value <= sdi_buf[prog_count+1];
				end
				endcase
				`CMD_STATE_SET(2)
				`DELAY42NSEC(5)
			end
			2: begin
				if (`CMD_IS(`CMD_READDATA)) begin
					sdo_buf[prog_count] <= zif[`DUT_SDIO];
				end
				prog_count <= prog_count + 1;
				`CMD_STATE_SET(3)
				`DELAY42NSEC(5)
			end
			3: begin
				dut_sci_auto <= 0;  /* CLK lo */

				if ((prog_count == 6 && `CMD_IS(`CMD_SENDINSTR)) ||
				    (prog_count == 16 && (`CMD_IS(`CMD_SENDDATA) ||
				    			  `CMD_IS(`CMD_READDATA)))) begin
					`CMD_FINISH
					prog_count <= 0;
					if (`CMD_IS(`CMD_SENDINSTR) ||
					    `CMD_IS(`CMD_SENDDATA)) begin
						dut_sdio_driven <= 0;
					end
					//dut_vpp <= 0;
				end else begin
					if (`CMD_IS(`CMD_READDATA)) begin
						`DELAY42NSEC(40)
					end  else begin
						`DELAY42NSEC(5)
					end
					`CMD_STATE_SET(0)
				end
			end
			endcase
		end
	`ASYNCPROC_END

	`DATAWRITE_BEGIN
		`ADDR(2): begin /* Run command */
			`CMD_RUN(in_data)
		end
		`ADDR(3): begin /* Load SDI LO BYTE sequence */
			sdi_buf[0] <= 0;
			sdi_buf[8:1] <= in_data;
		end
		`ADDR(4): begin /* Load SDI HI BYTE sequence */
			sdi_buf[12:9] <= in_data[3:0];
			sdi_buf[15:13] <= 0;
		end
		`ADDR(5): begin /* Set signals manually */
			dut_sci_manual <= in_data[0];  /* SCI */
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin /* Get SDO sequence high (bits 8-12) */
			out_data[3:0] <= sdo_buf[12:9];
			out_data[7:4] <= 0;
		end
		`ADDR(2): begin /* Read status */
			out_data[0] <= `CMD_IS_RUNNING;	/* busy */
			out_data[1] <= zif[`DUT_SDIO];	/* Raw SDO pin access */
		end
		`ADDR(3): begin /* Get SDO sequence low (bits 0-7) */
			out_data[7:0] <= sdo_buf[8:1];
		end
	`DATAREAD_END

	assign dut_sci = `CMD_IS_RUNNING ? dut_sci_auto : dut_sci_manual;

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)	`ZIF_UNUSED(5)	`ZIF_UNUSED(6)
	`ZIF_UNUSED(7)	`ZIF_UNUSED(8)	`ZIF_UNUSED(9)
	`ZIF_UNUSED(10)	`ZIF_UNUSED(11)	`ZIF_UNUSED(12)
	`ZIF_UNUSED(13)	`ZIF_UNUSED(14) `ZIF_UNUSED(15)
	`ZIF_UNUSED(16)	`ZIF_UNUSED(17) `ZIF_UNUSED(18)
	`ZIF_UNUSED(19)	
	bufif0(zif[20], high, low);				/* VCC */
	`ZIF_UNUSED(21)
	bufif0(zif[22], dut_sci, low);                          /* SCI */
	`ZIF_UNUSED(23)	`ZIF_UNUSED(24) `ZIF_UNUSED(25)
	`ZIF_UNUSED(26)
	bufif0(zif[27], dut_sdio_value, !dut_sdio_driven);      /* SDO */
	`ZIF_UNUSED(28)
	bufif0(zif[29], low, low);				/* GND */
	bufif0(zif[30], low, dut_vpp);      /* VPP/Reset */	
	`ZIF_UNUSED(31)	`ZIF_UNUSED(32)	`ZIF_UNUSED(33)
	`ZIF_UNUSED(34)
	`ZIF_UNUSED(35)	`ZIF_UNUSED(36)	`ZIF_UNUSED(37)
	`ZIF_UNUSED(38)	`ZIF_UNUSED(39)	`ZIF_UNUSED(40)
	`ZIF_UNUSED(41)	`ZIF_UNUSED(42)	`ZIF_UNUSED(43)
	`ZIF_UNUSED(44)	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)
	`ZIF_UNUSED(47)	`ZIF_UNUSED(48)
`BOTTOMHALF_END
