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
 * @ID_MAJOR: Major runtime ID (16 bit). Allocated in file 'RUNTIME_IDS'.
 * @ID_MINOR: Minor runtime ID (8 bit)
 */
`define BOTTOMHALF_BEGIN(NAME, ID_MAJOR, ID_MINOR)			\
	module NAME(__data, __ale, __write, __read, __osc, zif);	\
		inout [7:0] __data;					\
		input __ale;						\
		input __write;						\
		input __read;						\
		input __osc;						\
		inout [48:1] zif;					\
									\
		parameter __id_major = ID_MAJOR;			\
		parameter __id_minor = ID_MINOR;			\
									\
		reg [7:0] __addr_latch;					\
		reg [7:0] out_data;					\
		wire [7:0] in_data;					\
		assign in_data = __data;				\
									\
		wire __ale_signal;					\
		IBUFG __ale_ibufg(.I(__ale), .O(__ale_signal));		\
									\
		/* constant low/high signals */				\
		wire low, high;						\
		assign low = 0;						\
		assign high = 1;					\
									\
		/* Delay counter, based on 24MHz __osc. */		\
		reg [15:0] __delay_count;				\
		wire osc_signal;					\
		IBUF __osc_ibuf(.I(__osc), .O(osc_signal));		\
									\
		/* Command state */					\
		reg [1:0] __cmd_running;				\
		reg [7:0] __cmd;					\
		reg [7:0] __cmd_state;

/** BOTTOMHALF_END - End bottom-half module */
`define BOTTOMHALF_END							\
		always @(negedge __ale_signal) begin			\
			__addr_latch <= __data;				\
		end							\
									\
		wire __data_oe;						\
		assign __data_oe = !__read && __addr_latch[`ADDR_OK_BIT]; \
									\
		bufif0(__data[0], out_data[0], !__data_oe);		\
		bufif0(__data[1], out_data[1], !__data_oe);		\
		bufif0(__data[2], out_data[2], !__data_oe);		\
		bufif0(__data[3], out_data[3], !__data_oe);		\
		bufif0(__data[4], out_data[4], !__data_oe);		\
		bufif0(__data[5], out_data[5], !__data_oe);		\
		bufif0(__data[6], out_data[6], !__data_oe);		\
		bufif0(__data[7], out_data[7], !__data_oe);		\
	endmodule

/** INITIAL_BEGIN - Begin initialization section. */
`define INITIAL_BEGIN							\
	initial begin							\
		__addr_latch <= 0;					\
		out_data <= 0;						\
		__delay_count <= 0;					\
		__cmd_running <= 0;					\
		__cmd <= 0;						\
		__cmd_state <= 0;

/** INITIAL_END - End initialization section. */
`define INITIAL_END							\
	end /* initial */

/** INITIAL_NONE - Defines a dummy initial section. */
`define INITIAL_NONE							\
	`INITIAL_BEGIN							\
	`INITIAL_END

/** ASYNCPROC_BEGIN - Begin asynchronous OSC-based processing section. */
`define ASYNCPROC_BEGIN							\
	always @(posedge osc_signal) begin				\
		if (__delay_count == 0) begin				\
			/* Payload code follows... */

/** ASYNCPROC_END - End asynchronous section. */
`define ASYNCPROC_END							\
		end else begin						\
			__delay_count <= __delay_count - 1;		\
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
		default: begin end /* nothing */			\
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
		8'hFD: out_data <= __id_major;				\
		8'hFE: out_data <= __id_major >> 8;			\
		8'hFF: out_data <= __id_minor;				\
		default: out_data <= 0;					\
		endcase							\
	end /* always */

/** ZIF_BUF0 - Declare a ZIF buffer with negative outen.
 * @PIN: The pin number.
 * @OUT: The output signal.
 * @NOUTEN: The output enable signal, active low.
 */
`define ZIF_BUF0(PIN, OUT, NOUTEN)					\
	bufif0(zif[PIN], OUT, NOUTEN);

/** ZIF_BUF1 - Declare a ZIF buffer with positive outen.
 * @PIN: The pin number.
 * @OUT: The output signal.
 * @OUTEN: The output enable signal, active high.
 */
`define ZIF_BUF1(PIN, OUT, OUTEN)					\
	bufif1(zif[PIN], OUT, OUTEN);

/** ZIF_UNUSED - Declare a ZIF pin as unused.
 * @PIN: The pin number.
 * The ZIF pin is tied low.
 */
`define ZIF_UNUSED(PIN)							\
	`ZIF_BUF0(PIN, low, low)

/** CMD_RUN - Run a command.
 * @NR: The command number.
 */
`define CMD_RUN(NR)							\
	__cmd <= (NR);							\
	__cmd_running[0] <= ~__cmd_running[1];

/** CMD_RUNFLG_SYNC - Returns the synchronous run flag. */
`define CMD_RUNFLG_SYNC		__cmd_running[0]

/** CMD_RUNFLG_ASYNC - Returns the asynchronous run flag. */
`define CMD_RUNFLG_ASYNC	__cmd_running[1]

/** CMD_IS_RUNNING - Returns a boolean whether a command is running. */
`define CMD_IS_RUNNING		(`CMD_RUNFLG_SYNC ^ `CMD_RUNFLG_ASYNC)

/** CMD_NR - Returns the current command number. */
`define CMD_NR			__cmd

/** CMD_IS - Returns a boolean whether a certain command is running.
 * @NR: The command number to check.
 */
`define CMD_IS(NR)		(`CMD_IS_RUNNING && `CMD_NR == (NR))

/** CMD_FINISH - Finishes a command. */
`define CMD_FINISH							\
	__cmd_running[1] <= __cmd_running[0];				\
	__cmd_state <= 0;

/** CMD_STATE - Get command state. */
`define CMD_STATE	__cmd_state

/** CMD_STATE_SET - Set command state.
 * @VALUE: New value.
 */
`define CMD_STATE_SET(VALUE)						\
	__cmd_state <= (VALUE);

/* vim: filetype=verilog:shiftwidth=8:tabstop=8:softtabstop=8
 */
