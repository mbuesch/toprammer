/*
 *   TOP2049 Open Source programming suite
 *
 *   Universal device tester
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

`BOTTOMHALF_BEGIN(unitest, 8, 1)
	reg [47:0] zif_output_en;
	reg [47:0] zif_output;
	reg [47:0] zif_osc_en;
	reg zif_osc;

	reg [23:0] osc_divider;
	reg [23:0] osc_div_cnt;

	`INITIAL_NONE

	always @(posedge osc_signal) begin
		if (osc_div_cnt + 1 >= osc_divider) begin
			osc_div_cnt <= 0;
			zif_osc <= ~zif_osc;
		end else begin
			osc_div_cnt <= osc_div_cnt + 1;
		end
	end

	`DATAWRITE_BEGIN
		/* osc_divider is rightshifted by one and thus divided by two,
		 * because the oscillator always additionally divides by two. */
		`ADDR(8'h00):	osc_divider[6:0] <= in_data >> 1;
		`ADDR(8'h01):	osc_divider[14:7] <= in_data;
		`ADDR(8'h02):	osc_divider[22:15] <= in_data;
		`ADDR(8'h03):	osc_divider[23] <= in_data[0];

		`ADDR(8'h20):	zif_osc_en[7:0] <= in_data;
		`ADDR(8'h21):	zif_osc_en[15:8] <= in_data;
		`ADDR(8'h22):	zif_osc_en[23:16] <= in_data;
		`ADDR(8'h23):	zif_osc_en[31:24] <= in_data;
		`ADDR(8'h24):	zif_osc_en[39:32] <= in_data;
		`ADDR(8'h25):	zif_osc_en[47:40] <= in_data;

		`ADDR(8'h40):	zif_output_en[7:0] <= in_data;
		`ADDR(8'h41):	zif_output_en[15:8] <= in_data;
		`ADDR(8'h42):	zif_output_en[23:16] <= in_data;
		`ADDR(8'h43):	zif_output_en[31:24] <= in_data;
		`ADDR(8'h44):	zif_output_en[39:32] <= in_data;
		`ADDR(8'h45):	zif_output_en[47:40] <= in_data;

		`ADDR(8'h60):	zif_output[7:0] <= in_data;
		`ADDR(8'h61):	zif_output[15:8] <= in_data;
		`ADDR(8'h62):	zif_output[23:16] <= in_data;
		`ADDR(8'h63):	zif_output[31:24] <= in_data;
		`ADDR(8'h64):	zif_output[39:32] <= in_data;
		`ADDR(8'h65):	zif_output[47:40] <= in_data;
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(8'h60):	out_data <= zif[8:1];
		`ADDR(8'h61):	out_data <= zif[16:9];
		`ADDR(8'h62):	out_data <= zif[24:17];
		`ADDR(8'h63):	out_data <= zif[32:25];
		`ADDR(8'h64):	out_data <= zif[40:33];
		`ADDR(8'h65):	out_data <= zif[48:41];
	`DATAREAD_END

	bufif1(zif[1], zif_output[0] | (zif_osc & zif_osc_en[0]), zif_output_en[0]);
	bufif1(zif[2], zif_output[1] | (zif_osc & zif_osc_en[1]), zif_output_en[1]);
	bufif1(zif[3], zif_output[2] | (zif_osc & zif_osc_en[2]), zif_output_en[2]);
	bufif1(zif[4], zif_output[3] | (zif_osc & zif_osc_en[3]), zif_output_en[3]);
	bufif1(zif[5], zif_output[4] | (zif_osc & zif_osc_en[4]), zif_output_en[4]);
	bufif1(zif[6], zif_output[5] | (zif_osc & zif_osc_en[5]), zif_output_en[5]);
	bufif1(zif[7], zif_output[6] | (zif_osc & zif_osc_en[6]), zif_output_en[6]);
	bufif1(zif[8], zif_output[7] | (zif_osc & zif_osc_en[7]), zif_output_en[7]);
	bufif1(zif[9], zif_output[8] | (zif_osc & zif_osc_en[8]), zif_output_en[8]);
	bufif1(zif[10], zif_output[9] | (zif_osc & zif_osc_en[9]), zif_output_en[9]);
	bufif1(zif[11], zif_output[10] | (zif_osc & zif_osc_en[10]), zif_output_en[10]);
	bufif1(zif[12], zif_output[11] | (zif_osc & zif_osc_en[11]), zif_output_en[11]);
	bufif1(zif[13], zif_output[12] | (zif_osc & zif_osc_en[12]), zif_output_en[12]);
	bufif1(zif[14], zif_output[13] | (zif_osc & zif_osc_en[13]), zif_output_en[13]);
	bufif1(zif[15], zif_output[14] | (zif_osc & zif_osc_en[14]), zif_output_en[14]);
	bufif1(zif[16], zif_output[15] | (zif_osc & zif_osc_en[15]), zif_output_en[15]);
	bufif1(zif[17], zif_output[16] | (zif_osc & zif_osc_en[16]), zif_output_en[16]);
	bufif1(zif[18], zif_output[17] | (zif_osc & zif_osc_en[17]), zif_output_en[17]);
	bufif1(zif[19], zif_output[18] | (zif_osc & zif_osc_en[18]), zif_output_en[18]);
	bufif1(zif[20], zif_output[19] | (zif_osc & zif_osc_en[19]), zif_output_en[19]);
	bufif1(zif[21], zif_output[20] | (zif_osc & zif_osc_en[20]), zif_output_en[20]);
	bufif1(zif[22], zif_output[21] | (zif_osc & zif_osc_en[21]), zif_output_en[21]);
	bufif1(zif[23], zif_output[22] | (zif_osc & zif_osc_en[22]), zif_output_en[22]);
	bufif1(zif[24], zif_output[23] | (zif_osc & zif_osc_en[23]), zif_output_en[23]);
	bufif1(zif[25], zif_output[24] | (zif_osc & zif_osc_en[24]), zif_output_en[24]);
	bufif1(zif[26], zif_output[25] | (zif_osc & zif_osc_en[25]), zif_output_en[25]);
	bufif1(zif[27], zif_output[26] | (zif_osc & zif_osc_en[26]), zif_output_en[26]);
	bufif1(zif[28], zif_output[27] | (zif_osc & zif_osc_en[27]), zif_output_en[27]);
	bufif1(zif[29], zif_output[28] | (zif_osc & zif_osc_en[28]), zif_output_en[28]);
	bufif1(zif[30], zif_output[29] | (zif_osc & zif_osc_en[29]), zif_output_en[29]);
	bufif1(zif[31], zif_output[30] | (zif_osc & zif_osc_en[30]), zif_output_en[30]);
	bufif1(zif[32], zif_output[31] | (zif_osc & zif_osc_en[31]), zif_output_en[31]);
	bufif1(zif[33], zif_output[32] | (zif_osc & zif_osc_en[32]), zif_output_en[32]);
	bufif1(zif[34], zif_output[33] | (zif_osc & zif_osc_en[33]), zif_output_en[33]);
	bufif1(zif[35], zif_output[34] | (zif_osc & zif_osc_en[34]), zif_output_en[34]);
	bufif1(zif[36], zif_output[35] | (zif_osc & zif_osc_en[35]), zif_output_en[35]);
	bufif1(zif[37], zif_output[36] | (zif_osc & zif_osc_en[36]), zif_output_en[36]);
	bufif1(zif[38], zif_output[37] | (zif_osc & zif_osc_en[37]), zif_output_en[37]);
	bufif1(zif[39], zif_output[38] | (zif_osc & zif_osc_en[38]), zif_output_en[38]);
	bufif1(zif[40], zif_output[39] | (zif_osc & zif_osc_en[39]), zif_output_en[39]);
	bufif1(zif[41], zif_output[40] | (zif_osc & zif_osc_en[40]), zif_output_en[40]);
	bufif1(zif[42], zif_output[41] | (zif_osc & zif_osc_en[41]), zif_output_en[41]);
	bufif1(zif[43], zif_output[42] | (zif_osc & zif_osc_en[42]), zif_output_en[42]);
	bufif1(zif[44], zif_output[43] | (zif_osc & zif_osc_en[43]), zif_output_en[43]);
	bufif1(zif[45], zif_output[44] | (zif_osc & zif_osc_en[44]), zif_output_en[44]);
	bufif1(zif[46], zif_output[45] | (zif_osc & zif_osc_en[45]), zif_output_en[45]);
	bufif1(zif[47], zif_output[46] | (zif_osc & zif_osc_en[46]), zif_output_en[46]);
	bufif1(zif[48], zif_output[47] | (zif_osc & zif_osc_en[47]), zif_output_en[47]);
`BOTTOMHALF_END
