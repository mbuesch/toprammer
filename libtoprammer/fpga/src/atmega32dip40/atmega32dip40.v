/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel Mega32 DIP40
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2010-2012 Michael Buesch <m@bues.ch>
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

`BOTTOMHALF_BEGIN(atmega32dip40, 4, 1)
	reg dut_oe, dut_wr, dut_xtal, dut_pagel;
	reg dut_bs1, dut_bs2;
	reg dut_xa0, dut_xa1;
	reg [7:0] dut_data;
	reg dut_vpp_en;
	reg dut_vpp;
	reg dut_vcc_en;
	reg dut_vcc;

	`INITIAL_BEGIN
		dut_oe <= 0;
		dut_wr <= 0;
		dut_xtal <= 0;
		dut_pagel <= 0;
		dut_bs1 <= 0;
		dut_bs2 <= 0;
		dut_xa0 <= 0;
		dut_xa1 <= 0;
		dut_data <= 0;
		dut_vpp_en <= 0;
		dut_vpp <= 0;
		dut_vcc_en <= 0;
		dut_vcc <= 0;
	`INITIAL_END

	`ASYNCPROC_NONE

	`DATAWRITE_BEGIN
		`ADDR(0): begin
			/* Data write */
			dut_data <= in_data;
		end
		`ADDR(1): begin /* VCC/VPP control */
			dut_vpp_en <= in_data[0];
			dut_vpp <= in_data[1];
			dut_vcc_en <= in_data[2];
			dut_vcc <= in_data[3];
		end
		`ADDR(2): begin
			/* Control pin access */
			case (in_data[6:0])
			1: begin
				/* Unused */
			end
			2: begin
				dut_oe <= in_data[7];
			end
			3: begin
				dut_wr <= in_data[7];
			end
			4: begin
				dut_bs1 <= in_data[7];
			end
			5: begin
				dut_xa0 <= in_data[7];
			end
			6: begin
				dut_xa1 <= in_data[7];
			end
			7: begin
				dut_xtal <= in_data[7];
			end
			8: begin
				/* Unused */
			end
			9: begin
				dut_pagel <= in_data[7];
			end
			10: begin
				dut_bs2 <= in_data[7];
			end
			endcase
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin
			/* Data read */
			out_data <= zif[32:25];
		end
		`ADDR(2): begin
			/* Status read */
			out_data[0] <= zif[39];	/* RDY */
			out_data[7:1] <= 0;
		end
	`DATAREAD_END

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)
	bufif0(zif[5], dut_pagel, low);		/* PD7, PAGEL */
	bufif0(zif[6], low, high);		/* PC0 */
	bufif0(zif[7], low, high);		/* PC1 */
	bufif0(zif[8], low, high);		/* PC2 */
	bufif0(zif[9], low, high);		/* PC3 */
	bufif0(zif[10], low, high);		/* PC4 */
	bufif0(zif[11], low, high);		/* PC5 */
	bufif0(zif[12], low, high);		/* PC6 */
	bufif0(zif[13], low, high);		/* PC7 */
	bufif0(zif[14], dut_vcc, !dut_vcc_en);	/* AVCC */
	bufif0(zif[15], low, low);		/* GND */
	bufif0(zif[16], low, high);		/* AREF */
	bufif0(zif[17], low, high);		/* PA7 */
	bufif0(zif[18], low, high);		/* PA6 */
	bufif0(zif[19], low, high);		/* PA5 */
	bufif0(zif[20], low, high);		/* PA4 */
	bufif0(zif[21], low, high);		/* PA3 */
	bufif0(zif[22], low, high);		/* PA2 */
	bufif0(zif[23], low, high);		/* PA1 */
	bufif0(zif[24], dut_bs2, low);		/* PA0, BS2 */
	bufif0(zif[25], dut_data[0], !dut_oe);	/* PB0, DATA0 */
	bufif0(zif[26], dut_data[1], !dut_oe);	/* PB1, DATA1 */
	bufif0(zif[27], dut_data[2], !dut_oe);	/* PB2, DATA2 */
	bufif0(zif[28], dut_data[3], !dut_oe);	/* PB3, DATA3 */
	bufif0(zif[29], dut_data[4], !dut_oe);	/* PB4, DATA4 */
	bufif0(zif[30], dut_data[5], !dut_oe);	/* PB5, DATA5 */
	bufif0(zif[31], dut_data[6], !dut_oe);	/* PB6, DATA6 */
	bufif0(zif[32], dut_data[7], !dut_oe);	/* PB7, DATA7 */
	bufif0(zif[33], dut_vpp, !dut_vpp_en);	/* /RESET */
	bufif0(zif[34], dut_vcc, !dut_vcc_en);	/* VCC */
	bufif0(zif[35], low, low);		/* GND */
	bufif0(zif[36], low, high);		/* XTAL2 */
	bufif0(zif[37], dut_xtal, low);		/* XTAL1 */
	bufif0(zif[38], low, high);		/* PD0 */
	bufif0(zif[39], low, high);		/* PD1, RDY/BSY */
	bufif0(zif[40], dut_oe, low);		/* PD2, /OE */
	bufif0(zif[41], dut_wr, low);		/* PD3, /WR */
	bufif0(zif[42], dut_bs1, low);		/* PD4, BS1 */
	bufif0(zif[43], dut_xa0, low);		/* PD5, XA0 */
	bufif0(zif[44], dut_xa1, low);		/* PD6, XA1 */
	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)	`ZIF_UNUSED(47)
	`ZIF_UNUSED(48)
`BOTTOMHALF_END
