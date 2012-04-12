/*
 *   TOP2049 Open Source programming suite
 *
 *   FPGA bottom half - common macros
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

/** ADDR_OK_BIT - The "address OK" bit */
`define ADDR_OK_BIT	4

/** ADDR - Create a command address.
 * @BASE: The address base.
 */
`define ADDR(BASE)	((BASE) | (8'h01 << `ADDR_OK_BIT))

/** BOTTOMHALF_BEGIN - Begin bottom-half module
 * @NAME: The bitfile name
 * @TYPE: The type number (16 bit)
 * @SUBTYPE: The subtype number (8 bit)
 */
`define BOTTOMHALF_BEGIN(NAME, TYPE, SUBTYPE)				\
	module NAME(__data, __ale, __write, __read, __osc, zif);	\
		inout [7:0] __data;					\
		input __ale;						\
		input __write;						\
		input __read;						\
		input __osc;						\
		inout [48:1] zif;					\
									\
		parameter __type = TYPE;				\
		parameter __subtype = SUBTYPE;				\
									\
		reg [7:0] __addr_latch;					\
		reg [7:0] out_data;					\
		wire [7:0] in_data;					\
		assign in_data = __data;				\
									\
		/* constant low/high signals */				\
		wire low, high;						\
		assign low = 0;						\
		assign high = 1;					\
									\
		/* Delay counter, based on 24MHz __osc. */		\
		reg [15:0] __delay_count;				\
		wire osc_signal;					\
		IBUF __osc_ibuf(.I(__osc), .O(osc_signal));

/** BOTTOMHALF_END - End bottom-half module */
`define BOTTOMHALF_END							\
		initial begin						\
			__addr_latch <= 0;				\
			out_data <= 0;					\
		end							\
									\
		always @(negedge __ale) begin				\
			__addr_latch <= __data;				\
		end							\
									\
		wire __data_oe;						\
		assign __data_oe = !__read && __addr_latch[`ADDR_OK_BIT]; \
									\
		bufif1(__data[0], out_data[0], __data_oe);		\
		bufif1(__data[1], out_data[1], __data_oe);		\
		bufif1(__data[2], out_data[2], __data_oe);		\
		bufif1(__data[3], out_data[3], __data_oe);		\
		bufif1(__data[4], out_data[4], __data_oe);		\
		bufif1(__data[5], out_data[5], __data_oe);		\
		bufif1(__data[6], out_data[6], __data_oe);		\
		bufif1(__data[7], out_data[7], __data_oe);		\
	endmodule

/** ASYNCPROC_BEGIN - Begin asynchronous OSC-based processing section. */
`define ASYNCPROC_BEGIN							\
	always @(posedge osc_signal) begin				\
		if (__delay_count == 0) begin				\
			/* Payload code follows... */

/** ASYNCPROC_END - End asynchronous section. */
`define ASYNCPROC_END							\
		end else begin						\
			if (__delay_count != 0) begin			\
				__delay_count <= __delay_count - 1;	\
			end						\
		end /* if */						\
	end /* always */

/** ASYNCPROC_NONE - Defines a dummy asynchronous section. */
`define ASYNCPROC_NONE							\
	`ASYNCPROC_BEGIN						\
	`ASYNCPROC_END

/** UDELAY - Microsecond delay.
 * @USEC: Number of microseconds to delay. Maximum is 2730.
 */
`define UDELAY(USEC)	__delay_count <= (24 * USEC) - 1;

/** DATAWRITE_BEGIN - Begin "write" section.
 * The section body is the body of a "case" statement on the address.
 */
`define DATAWRITE_BEGIN							\
	always @(posedge __write) begin					\
		case (__addr_latch)

/** DATAWRITE_END - End "write" section. */
`define DATAWRITE_END							\
		endcase							\
	end /* always */

/** DATAREAD_BEGIN - Begin "read" section.
 * The section body is the body of a "case" statement on the address.
 */
`define DATAREAD_BEGIN							\
	always @(negedge __read) begin					\
		case (__addr_latch)

/** DATAREAD_END - End "read" section. */
`define DATAREAD_END							\
		8'hFD: out_data <= __type;				\
		8'hFE: out_data <= __type >> 8;				\
		8'hFF: out_data <= __subtype;				\
		endcase							\
	end /* always */

/** ZIF_UNUSED - Declare a ZIF pin as unused.
 * @PIN: The pin number.
 * The ZIF pin is tied low.
 */
`define ZIF_UNUSED(PIN)							\
	bufif0(zif[PIN], low, low);

/* vim: filetype=verilog:shiftwidth=8:tabstop=8:softtabstop=8
 */
