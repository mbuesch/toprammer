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
`include "microchip16.vh"

`undef DUT_SDIO
`define DUT_SDIO    17

`define DELAY42NSEC(D42NSEC)    __delay_count <= (D42NSEC) - 1;//41.666 ns wait cycle if D42NSEC = 1

`define CMD_SENDSIXINSTR    0
`define CMD_SENDREGOUTINSTR 1
`define CMD_ENTERPM 2
`define CMD_SEND9SIXINSTR    3
`define ENTERPM_SEQ 32'h4D434851

`ALL_WITHOUT_ZIF(microchip16dip14dip20, 32'hDF01, 1)

    `ZIF_UNUSED(1)
    `ZIF_UNUSED(2)
    `ZIF_UNUSED(3)
    `ZIF_UNUSED(4)
    `ZIF_UNUSED(5)
    `ZIF_UNUSED(6)
    `ZIF_UNUSED(7)
    `ZIF_UNUSED(8)
    `ZIF_UNUSED(9)
    `ZIF_UNUSED(10)
    `ZIF_UNUSED(11)
    `ZIF_UNUSED(12)
    `ZIF_UNUSED(13)
    `ZIF_UNUSED(14)
    bufif0(zif[15], low, dut_vpp);                             /* VPP/Reset */ 
    bufif0(zif[16], dut_sci, low);                             /* SCI - PGEC2 */
    bufif0(zif[17], dut_sdio_value, !dut_sdio_driven);         /* SDO - PGED2 */
    `ZIF_UNUSED(18)
    `ZIF_UNUSED(19) 
    `ZIF_UNUSED(20)
    `ZIF_UNUSED(21)
    `ZIF_UNUSED(22)
    `ZIF_UNUSED(23)
    `ZIF_UNUSED(24)
    `ZIF_UNUSED(25)
    `ZIF_UNUSED(26)
    `ZIF_UNUSED(27)
    `ZIF_UNUSED(28)
    `ZIF_UNUSED(29)
    `ZIF_UNUSED(30) 
    `ZIF_UNUSED(31)
    `ZIF_UNUSED(32)
    bufif0(zif[33], low, low);                                 /* GND */
    bufif0(zif[34], high, low);                                /* VCC */
    `ZIF_UNUSED(35)
    `ZIF_UNUSED(36)
    `ZIF_UNUSED(37)
    `ZIF_UNUSED(38)
    `ZIF_UNUSED(39)
    `ZIF_UNUSED(40)
    `ZIF_UNUSED(41)
    `ZIF_UNUSED(42)
    `ZIF_UNUSED(43)
    `ZIF_UNUSED(44)
    `ZIF_UNUSED(45)
    `ZIF_UNUSED(46)
    `ZIF_UNUSED(47)
    `ZIF_UNUSED(48) 
    
`BOTTOMHALF_END

/* vim: filetype=verilog:shiftwidth=8:tabstop=8:softtabstop=8
 */
