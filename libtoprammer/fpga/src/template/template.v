/*
 *   TOP2049 Open Source programming suite
 *
 *   XXXXXXXXXXXXXXXX
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) YEAR NAME
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

`BOTTOMHALF_BEGIN(template, 16'hCAFE, 42) /* TODO: <<< Adjust IDs here */
	reg examplereg;

	initial begin
		examplereg <= 0;
	end

	`ASYNCPROC_BEGIN
		/* TODO */
		examplereg <= ~examplereg;
		`UDELAY(42)
	`ASYNCPROC_END

	`DATAWRITE_BEGIN
		`ADDR(0): begin /* Write command 0 */
			/* TODO */
		end
		`ADDR(1): begin /* Write command 1 */
			/* TODO */
		end
	`DATAWRITE_END

	`DATAREAD_BEGIN
		`ADDR(0): begin /* Read command 0 */
			/* TODO */
		end
	`DATAREAD_END

	bufif0(zif[1], examplereg, low);
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
`BOTTOMHALF_END
