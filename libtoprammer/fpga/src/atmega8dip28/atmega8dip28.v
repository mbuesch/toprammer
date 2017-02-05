/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel Mega8 DIP28
 *   Atmel Mega88 DIP28
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

`BOTTOMHALF_BEGIN(atmega8dip28, 3, 1)
	reg oe, wr, xtal, pagel;
	reg bs1, bs2;
	reg xa0, xa1;
	reg [7:0] datap;
	reg vpp_en;
	reg vpp;
	reg vcc_en;
	reg vcc;

	`INITIAL_BEGIN
		oe <= 0;
		wr <= 0;
		xtal <= 0;
		pagel <= 0;
		bs1 <= 0;
		bs2 <= 0;
		xa0 <= 0;
		xa1 <= 0;
		datap <= 0;
		vpp_en <= 0;
		vpp <= 0;
		vcc_en <= 0;
		vcc <= 0;
	`INITIAL_END

	`ASYNCPROC_NONE

	`DATAWRITE_BEGIN
		`ADDR(0): begin
			/* Data write */
			datap <= in_data;
		end
		`ADDR(1): begin /* VCC/VPP control */
			vpp_en <= in_data[0];
			vpp <= in_data[1];
			vcc_en <= in_data[2];
			vcc <= in_data[3];
		end
		`ADDR(2): begin
			/* Control pin access */
			case (in_data[6:0])
			1: begin
				/* Unused */
			end
			2: begin
				oe <= in_data[7];
			end
			3: begin
				wr <= in_data[7];
			end
			4: begin
				bs1 <= in_data[7];
			end
			5: begin
				xa0 <= in_data[7];
			end
			6: begin
				xa1 <= in_data[7];
			end
			7: begin
				xtal <= in_data[7];
			end
			8: begin
				/* Unused */
			end
			9: begin
				pagel <= in_data[7];
			end
			10: begin
				bs2 <= in_data[7];
			end
			endcase
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin
			/* Data read */
			out_data[5:0] <= zif[29:24];
			out_data[7:6] <= zif[34:33];
		end
		`ADDR(2): begin
			/* Status read */
			out_data[0] <= zif[13];	/* RDY */
			out_data[7:1] <= 0;
		end
	`DATAREAD_END

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)	`ZIF_UNUSED(4)
	`ZIF_UNUSED(5)	`ZIF_UNUSED(6)	`ZIF_UNUSED(7)	`ZIF_UNUSED(8)
	`ZIF_UNUSED(9)	`ZIF_UNUSED(10)
	bufif0(zif[11], vpp, !vpp_en);		/* PC6, /RESET */
	bufif0(zif[12], low, high);		/* PD0 */
	bufif0(zif[13], low, high);		/* PD1, RDY/BSY */
	bufif0(zif[14], oe, low);		/* PD2, /OE */
	bufif0(zif[15], wr, low);		/* PD3, /WR */
	bufif0(zif[16], bs1, low);		/* PD4, BS1 */
	bufif0(zif[17], vcc, !vcc_en);		/* VCC */
	bufif0(zif[18], low, low);		/* GND */
	bufif0(zif[19], xtal, low);		/* PB6, XTAL1 */
	bufif0(zif[20], low, high);		/* PB7, XTAL2 */
	bufif0(zif[21], xa0, low);		/* PD5, XA0 */
	bufif0(zif[22], xa1, low);		/* PD6, XA1 */
	bufif0(zif[23], pagel, low);		/* PD7, PAGEL */
	bufif0(zif[24], datap[0], !oe);		/* PB0, DATA0 */
	bufif0(zif[25], datap[1], !oe);		/* PB1, DATA1 */
	bufif0(zif[26], datap[2], !oe);		/* PB2, DATA2 */
	bufif0(zif[27], datap[3], !oe);		/* PB3, DATA3 */
	bufif0(zif[28], datap[4], !oe);		/* PB4, DATA4 */
	bufif0(zif[29], datap[5], !oe);		/* PB5, DATA5 */
	bufif0(zif[30], vcc, !vcc_en);		/* AVCC */
	bufif0(zif[31], low, high);		/* AREF */
	bufif0(zif[32], low, low);		/* GND */
	bufif0(zif[33], datap[6], !oe);		/* PC0, DATA6 */
	bufif0(zif[34], datap[7], !oe);		/* PC1, DATA7 */
	bufif0(zif[35], bs2, low);		/* PC2, BS2 */
	bufif0(zif[36], low, high);		/* PC3 */
	bufif0(zif[37], low, high);		/* PC4 */
	bufif0(zif[38], low, high);		/* PC5 */
	`ZIF_UNUSED(39)	`ZIF_UNUSED(40)	`ZIF_UNUSED(41)	`ZIF_UNUSED(42)
	`ZIF_UNUSED(43)	`ZIF_UNUSED(44)	`ZIF_UNUSED(45)	`ZIF_UNUSED(46)
	`ZIF_UNUSED(47)	`ZIF_UNUSED(48)
`BOTTOMHALF_END
