/*
 *   TOP2049 Open Source programming suite
 *
 *   Simple frequency counter
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2012 Michael Buesch <m@bues.ch>
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

`BOTTOMHALF_BEGIN(unitest_fcnt, 8, 2)
	reg [35:12] zif_output_en;
	reg [35:12] zif_output;
	reg [35:12] zif_osc_en;
	reg zif_osc;

	reg [23:0] osc_divider;
	reg [23:0] osc_div_cnt;

	reg [5:0] fcnt_sel;
	reg fcnt_invert;
	wire fcnt_state;
	reg fcnt_last_state;
	reg [27:0] fcnt_count;
	reg [27:0] fcnt_saved_count;

	`INITIAL_NONE

	always @(posedge osc_signal) begin
		if (osc_div_cnt + 1 >= osc_divider) begin
			osc_div_cnt <= 0;
			zif_osc <= ~zif_osc;
		end else begin
			osc_div_cnt <= osc_div_cnt + 1;
		end
	end

	assign fcnt_state = (fcnt_sel <= 47) ? (zif[fcnt_sel + 1] ^ fcnt_invert) : 0;

	always @(negedge osc_signal) begin
		if (fcnt_state & ~fcnt_last_state) begin
			fcnt_saved_count <= fcnt_count + 1;
			fcnt_count <= 0;
		end else begin
			fcnt_count <= fcnt_count + 1;
		end
		fcnt_last_state <= fcnt_state;
	end

	`DATAWRITE_BEGIN
		/* osc_divider is rightshifted by one and thus divided by two,
		 * because the oscillator always additionally divides by two. */
		`ADDR(8'h00):	osc_divider[6:0] <= in_data >> 1;
		`ADDR(8'h01):	osc_divider[14:7] <= in_data;
		`ADDR(8'h02):	osc_divider[22:15] <= in_data;
		`ADDR(8'h03):	osc_divider[23] <= in_data[0];

		`ADDR(8'h20):	;
		`ADDR(8'h21):	zif_osc_en[15:12] <= in_data[7:4];
		`ADDR(8'h22):	zif_osc_en[23:16] <= in_data;
		`ADDR(8'h23):	zif_osc_en[31:24] <= in_data;
		`ADDR(8'h24):	zif_osc_en[35:32] <= in_data[3:0];
		`ADDR(8'h25):	;

		`ADDR(8'h40):	;
		`ADDR(8'h41):	zif_output_en[15:12] <= in_data[7:4];
		`ADDR(8'h42):	zif_output_en[23:16] <= in_data;
		`ADDR(8'h43):	zif_output_en[31:24] <= in_data;
		`ADDR(8'h44):	zif_output_en[35:32] <= in_data[3:0];
		`ADDR(8'h45):	;

		`ADDR(8'h60):	;
		`ADDR(8'h61):	zif_output[15:12] <= in_data[7:4];
		`ADDR(8'h62):	zif_output[23:16] <= in_data;
		`ADDR(8'h63):	zif_output[31:24] <= in_data;
		`ADDR(8'h64):	zif_output[35:32] <= in_data[3:0];
		`ADDR(8'h65):	;

		`ADDR(8'h80): begin
			fcnt_sel[5:0] <= in_data[5:0];
			fcnt_invert <= in_data[7];
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(8'h00):	out_data <= fcnt_saved_count[7:0];
		`ADDR(8'h01):	out_data <= fcnt_saved_count[15:8];
		`ADDR(8'h02):	out_data <= fcnt_saved_count[23:16];
		`ADDR(8'h03):	out_data <= fcnt_saved_count[27:24];

//		`ADDR(8'h60):	out_data <= 0;
		`ADDR(8'h61):	out_data <= zif[16:13] << 4;
		`ADDR(8'h62):	out_data <= zif[24:17];
		`ADDR(8'h63):	out_data <= zif[32:25];
		`ADDR(8'h64):	out_data <= zif[36:33];
//		`ADDR(8'h65):	out_data <= 0;
	`DATAREAD_END

	`ZIF_UNUSED(1)	`ZIF_UNUSED(2)	`ZIF_UNUSED(3)
	`ZIF_UNUSED(4)	`ZIF_UNUSED(5)	`ZIF_UNUSED(6)
	`ZIF_UNUSED(7)	`ZIF_UNUSED(8)	`ZIF_UNUSED(9)
	`ZIF_UNUSED(10)	`ZIF_UNUSED(11)	`ZIF_UNUSED(12)
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
	`ZIF_UNUSED(37)	`ZIF_UNUSED(38)	`ZIF_UNUSED(39)
	`ZIF_UNUSED(40)	`ZIF_UNUSED(41)	`ZIF_UNUSED(42)
	`ZIF_UNUSED(43)	`ZIF_UNUSED(44)	`ZIF_UNUSED(45)
	`ZIF_UNUSED(46)	`ZIF_UNUSED(47)	`ZIF_UNUSED(48)
`BOTTOMHALF_END
