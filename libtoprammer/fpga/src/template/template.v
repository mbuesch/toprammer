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

	`INITIAL_BEGIN
		examplereg <= 0;
	`INITIAL_END

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

	`ZIF_BUF0(1, examplereg, low);
	`ZIF_BUF0(2, low, low);
	`ZIF_BUF0(3, low, low);
	`ZIF_BUF0(4, low, low);
	`ZIF_BUF0(5, low, low);
	`ZIF_BUF0(6, low, low);
	`ZIF_BUF0(7, low, low);
	`ZIF_BUF0(8, low, low);
	`ZIF_BUF0(9, low, low);
	`ZIF_BUF0(10, low, low);
	`ZIF_BUF0(11, low, low);
	`ZIF_BUF0(12, low, low);
	`ZIF_BUF0(13, low, low);
	`ZIF_BUF0(14, low, low);
	`ZIF_BUF0(15, low, low);
	`ZIF_BUF0(16, low, low);
	`ZIF_BUF0(17, low, low);
	`ZIF_BUF0(18, low, low);
	`ZIF_BUF0(19, low, low);
	`ZIF_BUF0(20, low, low);
	`ZIF_BUF0(21, low, low);
	`ZIF_BUF0(22, low, low);
	`ZIF_BUF0(23, low, low);
	`ZIF_BUF0(24, low, low);
	`ZIF_BUF0(25, low, low);
	`ZIF_BUF0(26, low, low);
	`ZIF_BUF0(27, low, low);
	`ZIF_BUF0(28, low, low);
	`ZIF_BUF0(29, low, low);
	`ZIF_BUF0(30, low, low);
	`ZIF_BUF0(31, low, low);
	`ZIF_BUF0(32, low, low);
	`ZIF_BUF0(33, low, low);
	`ZIF_BUF0(34, low, low);
	`ZIF_BUF0(35, low, low);
	`ZIF_BUF0(36, low, low);
	`ZIF_BUF0(37, low, low);
	`ZIF_BUF0(38, low, low);
	`ZIF_BUF0(39, low, low);
	`ZIF_BUF0(40, low, low);
	`ZIF_BUF0(41, low, low);
	`ZIF_BUF0(42, low, low);
	`ZIF_BUF0(43, low, low);
	`ZIF_BUF0(44, low, low);
	`ZIF_BUF0(45, low, low);
	`ZIF_BUF0(46, low, low);
	`ZIF_BUF0(47, low, low);
	`ZIF_BUF0(48, low, low);
`BOTTOMHALF_END
