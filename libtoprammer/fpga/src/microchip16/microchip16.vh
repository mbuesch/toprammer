/*
 *   TOP2049 Open Source programming suite
 *
 *   Microchip header file for 16 bit MCUs
 *   FPGA Main bottomhalf implementation
 *
 *   Copyright (c) 2013 Pavel Stemberk <stemberk@gmail.com>
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

`define DUT_SDIO    35

`define DELAY42NSEC(D42NSEC)    __delay_count <= (D42NSEC) - 1;//41.666 ns wait cycle if D42NSEC = 1

`define CMD_SENDSIXINSTR    0
`define CMD_SENDREGOUTINSTR 1
`define CMD_ENTERPM 2
`define CMD_SEND9SIXINSTR    3
`define ENTERPM_SEQ 32'h4D434851

`define ALL_WITHOUT_ZIF(NAME_, ID_MAJOR_, ID_MINOR_)	\
`BOTTOMHALF_BEGIN(NAME_,ID_MAJOR_, ID_MINOR_)          \
    /* Programmer context */                    \
    reg [7:0] prog_count;                       \
    reg dut_sci_manual;                     \
    reg dut_sci_auto;                       \
    wire dut_sci;                           \
    reg dut_sdio_driven_manual;                     \
    reg dut_sdio_driven_auto;                       \
    wire dut_sdio_driven;                   \
    reg dut_sdio_value_manual;                      \
    reg dut_sdio_value_auto;                        \
    wire dut_sdio_value;                        \
    reg dut_vpp;                            \
    reg [23:0] sdi_buf;                     \
    reg [15:0] sdo_buf;                     \
    reg [31:0] enterpm_seq;                 \
    reg sdio_auto;\
    reg [3:0] dly5;                         \
    reg [7:0] tdly;                                                  \
                                \
    `INITIAL_BEGIN                           \
        prog_count <= 0;                    \
        dut_sci_manual <= 0;                    \
        dut_sci_auto <= 0;                  \
        dut_sdio_driven_auto <= 0;                  \
        dut_sdio_driven_manual <= 0;                    \
        dut_sdio_value_auto <= 0;                   \
        dut_sdio_value_manual <= 0;                 \
        sdi_buf <= 0;                       \
        sdo_buf <= 0;                       \
        dut_vpp <= 0;                       \
        sdio_auto <= 1;                     \
        enterpm_seq <= `ENTERPM_SEQ ;\
        tdly <= 24;                         \
        dly5 <= 5;                                 \
    `INITIAL_END                             \
                                \
    `ASYNCPROC_BEGIN                        \
        if (`CMD_IS_RUNNING) begin              \
            case (`CMD_STATE)               \
            0: begin                    \
                case(`CMD_NR)\
                `CMD_SENDSIXINSTR: begin            \
                    dut_sdio_driven_auto <= 1;     \
                    if (prog_count > 3) begin      \
                        dut_sdio_value_auto <= sdi_buf[prog_count-4];\
                    end                             \
                end               \
                `CMD_SEND9SIXINSTR: begin            \
                    dut_sdio_driven_auto <= 1;     \
                    if (prog_count > 8) begin      \
                        dut_sdio_value_auto <= sdi_buf[prog_count-9];\
                    end                             \
                end                 \
                `CMD_SENDREGOUTINSTR: begin         \
                    if (prog_count == 0) begin      \
                        dut_sdio_value_auto <= 1;        \
                    end else begin                  \
                        dut_sdio_value_auto <= 0;        \
                    end                             \
                    if (prog_count < 4 ) begin  \
                        dut_sdio_driven_auto <= 1;      \
                    end else begin              \
                        dut_sdio_driven_auto <= 0;      \
                    end                 \
                end                 \
                `CMD_ENTERPM: begin            \
                    dut_sdio_driven_auto <= 1;      \
                    dut_sdio_value_auto <= enterpm_seq[31-prog_count];\
                end                 \
                endcase                 \
                `CMD_STATE_SET(1)           \
                `DELAY42NSEC(dly5)             \
            end                     \
            1: begin                \
                dut_sci_auto <= 1;      \
                if (`CMD_IS(`CMD_SENDREGOUTINSTR) && prog_count > 11 && prog_count < 28) begin  \
                    sdo_buf[prog_count-12] <= zif[`DUT_SDIO];\
                end                 \
                `CMD_STATE_SET(2)           \
                `DELAY42NSEC(dly5)             \
            end                     \
            2: begin                    \
                prog_count <= prog_count + 1;       \
                `CMD_STATE_SET(3)           \
                `DELAY42NSEC(dly5)             \
            end                     \
            3: begin                    \
                dut_sci_auto <= 0;  /* CLK lo */    \
                                    \
                if (\
                    (prog_count == 32 && `CMD_IS(`CMD_ENTERPM)) ||\
                    (prog_count == 33 && `CMD_IS(`CMD_SEND9SIXINSTR)) ||\
                    (prog_count == 28 && (`CMD_IS(`CMD_SENDREGOUTINSTR) || `CMD_IS(`CMD_SENDSIXINSTR)))\
                ) begin \
                    `CMD_FINISH             \
                    prog_count <= 0;        \
                    dut_sdio_value_auto <= 0;        \
                end else begin\
                    if(`CMD_IS(`CMD_SENDREGOUTINSTR) && prog_count == 12 ) begin\
                        `DELAY42NSEC(tdly)\
                    end else begin              \
                        `DELAY42NSEC(dly5) \
                    end    \
                    `CMD_STATE_SET(0)       \
                end                 \
            end                     \
            endcase                     \
        end                         \
    `ASYNCPROC_END                          \
                                    \
    `DATAWRITE_BEGIN                        \
        `ADDR(0): begin /* Set dly5 - base clock period half, 1=42ns*/      \
                dly5 <= in_data[3:0];           \
            end                         \
        `ADDR(1): begin /* Set tdly - REGOUT: delay between command and data 1=42ns*/       \
                tdly <= in_data;                \
            end                                                  \
        `ADDR(2): begin /* Run command */           \
            `CMD_RUN(in_data)               \
            sdio_auto <= 1;                 \
        end\
        `ADDR(3): begin /* Load SDI LO BYTE sequence */     \
            sdi_buf[7:0] <= in_data;            \
        end                         \
        `ADDR(4): begin /* Load SDI ME BYTE sequence */     \
            sdi_buf[15:8] <= in_data;           \
        end                         \
        `ADDR(5): begin /* Load SDI HI BYTE sequence */     \
            sdi_buf[23:16] <= in_data;          \
        end                         \
        `ADDR(9): begin /* Set signals manually */      \
            dut_sci_manual <= in_data[0];  /* SCI */    \
            dut_sdio_driven_manual <= in_data[1];  /* SDIODRIVEN */ \
            dut_sdio_value_manual <= in_data[2];  /* SDIOVALUE */   \
            sdio_auto <= 0;                 \
    end                         \
    `DATAWRITE_END                          \
                                    \
    `DATAREAD_BEGIN                         \
        `ADDR(0): begin /* Get SDO sequence high (bits 8-13) */ \
            out_data[7:0] <= sdo_buf[15:8];            \
        end                         \
        `ADDR(2): begin /* Read status */           \
            out_data[0] <= `CMD_IS_RUNNING; /* busy */  \
            out_data[1] <= zif[`DUT_SDIO];  /* Raw SDO pin access */\
        end                         \
        `ADDR(3): begin /* Get SDO sequence low (bits 0-7) */   \
            out_data[7:0] <= sdo_buf[7:0];      \
        end                         \
    `DATAREAD_END                           \
                                    \
    assign dut_sci = `CMD_IS_RUNNING ? dut_sci_auto : dut_sci_manual;   \
    assign dut_sdio_driven = sdio_auto?dut_sdio_driven_auto:dut_sdio_driven_manual; \
    assign dut_sdio_value =  sdio_auto?dut_sdio_value_auto:dut_sdio_value_manual;

/* vim: filetype=verilog:shiftwidth=8:tabstop=8:softtabstop=8
 */
