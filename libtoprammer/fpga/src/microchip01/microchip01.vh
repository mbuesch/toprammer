/*
 *   TOP2049 Open Source programming suite
 *
 *   Microchip - version 01
 *   FPGA Main bottomhalf implementation
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

`define CMDBIT_4BITINSTR	0
`define CMDBIT_SENDDATA	1
`define CMDBIT_READDATA	2
`define DATBIT_KEEPCLKHIGH 4
`define ALL_WITHOUT_ZIF(NAME_, ID_MAJOR_, ID_MINOR_)			\
    `BOTTOMHALF_BEGIN(NAME_, ID_MAJOR_, ID_MINOR_)			\
    	/* Programmer context */					\
    	reg [4:0] prog_count;						\
    	reg dut_sci_manual;						\
    	reg dut_sci_auto;						\
    	wire dut_sci;							\
    	reg dut_sdio_driven_manual;						\
    	reg dut_sdio_driven_auto;						\
    	wire dut_sdio_driven;					\
    	reg dut_sdio_value_manual;						\
    	reg dut_sdio_value_auto;						\
    	wire dut_sdio_value;						\
    	reg dut_vpp;							\
    	reg [15:0] sdi_buf;						\
    	reg [15:0] sdo_buf;						\
    	reg [5:0] instr;						\
    	reg [3:0] dly5;							\
    	reg [7:0] tdly;							\
    	reg sdio_auto;							\
    	wire is_command;						\
									\
    	`INITIAL_BEGIN							\
    		prog_count <= 0;					\
    		dut_sci_manual <= 0;					\
    		dut_sci_auto <= 0;					\
    		dut_sdio_driven_auto <= 0;					\
    		dut_sdio_driven_manual <= 0;					\
    		dut_sdio_value_auto <= 0;					\
    		dut_sdio_value_manual <= 0;					\
    		sdi_buf <= 0;						\
    		sdo_buf <= 0;						\
    		instr <= 0;							\
    		dut_vpp <= 0;						\
    		tdly <=	24;							\
    		dly5 <=	5;							\
		sdio_auto <= 1;						\
    	`INITIAL_END							\
									\
    	`ASYNCPROC_BEGIN						\
    		if (`CMD_IS_RUNNING) begin				\
    			case (`CMD_STATE)				\
    			0: begin					\
    				if ( \
    					 !is_command && `CMD_NR[`CMDBIT_READDATA] \
    				) begin	\
    					dut_sdio_driven_auto <= 0;		\
    				end else begin				\
    					dut_sdio_driven_auto <= 1;		\
    				end					\
					if((prog_count == 4 && `CMD_NR[`CMDBIT_4BITINSTR]) || (prog_count == 6 && !`CMD_NR[`CMDBIT_4BITINSTR])) begin \
						dut_sdio_value_auto <= 0; \
					end \
    				`CMD_STATE_SET(1)			\
    				`DELAY42NSEC(dly5)				\
    			end						\
    			1: begin					\
    				dut_sci_auto <= 1;  /* CLK hi  80ns after this moment we need to be prepared in CMD_READDATA case */	\
    				if(is_command) begin			\
    					dut_sdio_value_auto <= instr[prog_count];\
    				end else if(`CMD_NR[`CMDBIT_SENDDATA]) begin			\
    					dut_sdio_value_auto <= sdi_buf[`CMD_NR[`CMDBIT_4BITINSTR]? prog_count-4 : prog_count-6];\
    				end					\
    				`CMD_STATE_SET(2)			\
    				`DELAY42NSEC(dly5)				\
    			end						\
    			2: begin					\
    				if (!is_command && `CMD_NR[`CMDBIT_READDATA]) begin	\
    					sdo_buf[`CMD_NR[`CMDBIT_4BITINSTR]? prog_count-4 : prog_count-6] <= zif[`DUT_SDIO];\
    				end					\
    				prog_count <= prog_count + 1;		\
    				`CMD_STATE_SET(3)			\
    				`DELAY42NSEC(dly5)				\
    			end						\
    			3: begin					\
    				if (					\
					(!`CMD_NR[`CMDBIT_READDATA] && !`CMD_NR[`CMDBIT_SENDDATA] && \
						(			\
    							(prog_count == 4 && `CMD_NR[`CMDBIT_4BITINSTR]) || (prog_count == 6 && !`CMD_NR[`CMDBIT_4BITINSTR]) \
    						)			\
    					) || (\
						(`CMD_NR[`CMDBIT_READDATA] || `CMD_NR[`CMDBIT_SENDDATA]) && \
						(			\
							(prog_count == 20 && `CMD_NR[`CMDBIT_4BITINSTR]) || (prog_count == 22 && !`CMD_NR[`CMDBIT_4BITINSTR]) \
						)			\
					)				\
					) begin				\
						if(`CMD_NR[`CMDBIT_4BITINSTR] && instr[`DATBIT_KEEPCLKHIGH]) begin \
							dut_sci_auto <= 1;  /* keep CLK high for 4bit instruction commands if is it requested */	\
						end else begin		\
							dut_sci_auto <= 0;  /* CLK lo */	\
						end					\
						if(`CMD_NR[`CMDBIT_4BITINSTR])	\
						begin				\
							`CMD_STATE_SET(4)	\
							`DELAY42NSEC(dly5) 	\
						end else begin			\
							`CMD_FINISH			\
							prog_count <= 0;		\
							dut_sdio_driven_auto <= 1;	\
							dut_sdio_value_auto <= 0;	\
						end				\
    				end else begin				\
    					dut_sci_auto <= 0;  /* CLK lo */	\
    					if((prog_count == 4 && `CMD_NR[`CMDBIT_4BITINSTR]) || (prog_count == 6 && !`CMD_NR[`CMDBIT_4BITINSTR])) begin \
    						`DELAY42NSEC(tdly) \
    					end else begin \
    						`DELAY42NSEC(dly5) \
    					end \
    					`CMD_STATE_SET(0)		\
    				end					\
    			end						\
			4: begin					\
    					`CMD_FINISH			\
					prog_count <= 0;		\
					dut_sdio_driven_auto <= 1;	\
					dut_sdio_value_auto <= 0;	\
			end						\
    			endcase						\
    		end							\
    	`ASYNCPROC_END							\
    									\
    	`DATAWRITE_BEGIN						\
    		`ADDR(0): begin /* Set dly5 - base clock period half, 1=42ns*/		\
    			dly5 <= in_data[3:0];			\
    		end							\
    		`ADDR(1): begin /* Set tdly - delay between command and data 1=42ns*/		\
    			tdly <= in_data;				\
    		end							\
    		`ADDR(2): begin /* Run any command */		\
    			instr[4:0] <= in_data[7:3];				\
			if(in_data[`CMDBIT_4BITINSTR]) 				\
			begin							\
				dut_sci_manual <= in_data[7];			\
			end							\
    			`CMD_RUN(in_data & 8'h07)				\
				sdio_auto <= 1;					\
    		end							\
    		`ADDR(3): begin /* Load 14bit SDI LO BYTE sequence */		\
    			sdi_buf[0] <= 0;				\
    			sdi_buf[8:1] <= in_data;			\
    		end							\
    		`ADDR(4): begin /* Load 14bit SDI HI BYTE sequence */		\
    			sdi_buf[14:9] <= in_data[5:0];			\
    			sdi_buf[15] <= 0;				\
    		end							\
    		`ADDR(5): begin /* Set signals manually */		\
    			dut_sci_manual <= in_data[0];  /* SCI */	\
    			dut_sdio_driven_manual <= in_data[1];  /* SDIODRIVEN */	\
    			dut_sdio_value_manual <= in_data[2];  /* SDIOVALUE */	\
				sdio_auto <= 0;					\
    		end							\
    		`ADDR(6): begin /* Load 16bit SDI LO BYTE sequence */		\
    			sdi_buf[7:0] <= in_data;			\
    		end							\
    		`ADDR(7): begin /* Load 16bit SDI HI BYTE sequence */		\
    			sdi_buf[15:8] <= in_data;			\
    		end							\
    	`DATAWRITE_END							\
    									\
    	`DATAREAD_BEGIN							\
    		`ADDR(0): begin /* Get 14bit SDO sequence high (bits 8-13) */	\
    			out_data[5:0] <= sdo_buf[14:9];			\
    			out_data[7:6] <= 0;				\
    		end							\
    		`ADDR(2): begin /* Read status */			\
    			out_data[0] <= `CMD_IS_RUNNING;	/* busy */	\
    			out_data[1] <= zif[`DUT_SDIO];	/* Raw SDO pin access */\
    		end							\
    		`ADDR(3): begin /* Get 14bit SDO sequence low (bits 0-7) */	\
    			out_data[7:0] <= sdo_buf[8:1];			\
    		end							\
    		`ADDR(4): begin /* Get 16bit SDO sequence high (bits 8-13) */	\
    			out_data[7:0] <= sdo_buf[15:8];			\
    		end							\
    		`ADDR(5): begin /* Get 16bit SDO sequence low (bits 0-7) */	\
    			out_data[7:0] <= sdo_buf[7:0];		\
    		end							\
    	`DATAREAD_END							\
    									\
		assign dut_sci = `CMD_IS_RUNNING ? dut_sci_auto : dut_sci_manual;\
		assign dut_sdio_driven = sdio_auto?dut_sdio_driven_auto:dut_sdio_driven_manual;	\
		assign dut_sdio_value =  sdio_auto?dut_sdio_value_auto:dut_sdio_value_manual;	\
		assign is_command = (`CMD_NR[`CMDBIT_4BITINSTR] && prog_count < 4) || (!`CMD_NR[`CMDBIT_4BITINSTR] && prog_count < 6);

/* vim: filetype=verilog:shiftwidth=8:tabstop=8:softtabstop=8
 */
