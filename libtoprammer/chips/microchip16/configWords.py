"""
#    TOP2049 Open Source programming suite
#
#    configWordsSet - configWord specification for 16bit PIC MCUs
#
#    Copyright (c) 2014 Pavel Stemberk <stemberk@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from  libtoprammer.chip import BitDescription

ka200_fuseDesc = (
	BitDescription(0o00, "NA"),
	BitDescription(0o01, "NA"),
	BitDescription(0o02, "NA"),
	BitDescription(0o03, "NA"),
	BitDescription(0o04, "NA"),
	BitDescription(0o05, "NA"),
	BitDescription(0o06, "NA"),
	BitDescription(0o07, "NA"),
	BitDescription(0o10, "NA"),
	BitDescription(0o11, "NA"),
	BitDescription(0o12, "NA"),
	BitDescription(0o13, "NA"),
	BitDescription(0o14, "NA"),
	BitDescription(0o15, "NA"),
	BitDescription(0o16, "NA"),
	BitDescription(0o17, "NA"),
	
	BitDescription(0o20, "NA"),
	BitDescription(0o21, "NA"),
	BitDescription(0o22, "NA"),
	BitDescription(0o23, "NA"),
	BitDescription(0o24, "NA"),
	BitDescription(0o25, "NA"),
	BitDescription(0o26, "NA"),
	BitDescription(0o27, "NA"),
	BitDescription(0o30, "NA"),
	BitDescription(0o31, "NA"),
	BitDescription(0o32, "NA"),
	BitDescription(0o33, "NA"),
	BitDescription(0o34, "NA"),
	BitDescription(0o35, "NA"),
	BitDescription(0o36, "NA"),
	BitDescription(0o37, "NA"),
	
	BitDescription(0o40, "FGS:GWRP: General Segment Code Flash Write Protection bit, 1 = General segment may be written"),
	BitDescription(0o41, "FGS:GSS0 General Segment Code Flash Code Protection bit, 1 = no protection"),
	BitDescription(0o42, "NA"),
	BitDescription(0o43, "NA"),
	BitDescription(0o44, "NA"),
	BitDescription(0o45, "NA"),
	BitDescription(0o46, "NA"),
	BitDescription(0o47, "NA"),
	BitDescription(0o50, "NA"),
	BitDescription(0o51, "NA"),
	BitDescription(0o52, "NA"),
	BitDescription(0o53, "NA"),
	BitDescription(0o54, "NA"),
	BitDescription(0o55, "NA"),
	BitDescription(0o56, "NA"),
	BitDescription(0o57, "NA"),
	
	BitDescription(0o60, "FOSCSEL: FNOSC[0] 101 = 500 kHz Low-Power FRC oscillato"),
	BitDescription(0o61, "FOSCSEL: FNOSC[1] 110 = 500 kHz Low-Power FRC oscillator with divide-by-N (LPFRCDIV)"),
	BitDescription(0o62, "FOSCSEL: FNOSC[2] 111 = 8 MHz FRC oscillator with divide-by-N (FRCDIV)"),
	BitDescription(0o63, "NA"),
	BitDescription(0o64, "NA"),
	BitDescription(0o65, "NA"),
	BitDescription(0o66, "NA"),
	BitDescription(0o67, "FOSCSEL: IESO: Internal External Switchover bit, 1 = enabled"),
	BitDescription(0o70, "NA"),
	BitDescription(0o71, "NA"),
	BitDescription(0o72, "NA"),
	BitDescription(0o73, "NA"),
	BitDescription(0o74, "NA"),
	BitDescription(0o75, "NA"),
	BitDescription(0o76, "NA"),
	BitDescription(0o77, "NA"),
	
	BitDescription(0o100, "FOSC: POSCMD[0] 11 = Primary oscillator disabled = HS Oscillator mode selected"),
	BitDescription(0o101, "FOSC: POSCMD[1]"),
	BitDescription(0o102, "FOSC: OSCIOFNC 1 = CLKO output signal active on the OSCO pin"),
	BitDescription(0o103, "FOSC: POSCFREQ[0] 00 = Reserved; do not use"),
	BitDescription(0o104, "FOSC: POSCFREQ[1] 11 = Primary oscillator/external clock input frequency greater than 8 MHz"),
	BitDescription(0o105, "FOSC: SOSCSEL 1 = Secondary oscillator configured for high-power operation"),
	BitDescription(0o106, "FOSC: FCKSM[0] 00 = Clock switching is enabled, Fail-Safe Clock Monitor is enabled"),
	BitDescription(0o107, "FOSC: FCKSM[1] 1x = Clock switching is disabled, Fail-Safe Clock Monitor is disabled"),
	BitDescription(0o110, "NA"),
	BitDescription(0o111, "NA"),
	BitDescription(0o112, "NA"),
	BitDescription(0o113, "NA"),
	BitDescription(0o114, "NA"),
	BitDescription(0o115, "NA"),
	BitDescription(0o116, "NA"),
	BitDescription(0o117, "NA"), 	
    
	BitDescription(0o120, "FWDT: WDTPS[0] 0000 = 1:1"),
	BitDescription(0o121, "FWDT: WDTPS[1] 0001 = 1:2"),
	BitDescription(0o122, "FWDT: WDTPS[2] 0010 = 1:4"),
	BitDescription(0o123, "FWDT: WDTPS[3] 1111 = 1:32768"),
	BitDescription(0o124, "FWDT: FWPSA 1 = WDT prescaler ratio of 1:128"),
	BitDescription(0o125, "NA"),
	BitDescription(0o126, "FWDT: WINDIS: 1 = Standard WDT selected; windowed WDT disabled"),
	BitDescription(0o127, "FWDT: FWDTEN: 1 = WDT enabled"),
	BitDescription(0o130, "NA"),
	BitDescription(0o131, "NA"),
	BitDescription(0o132, "NA"),
	BitDescription(0o133, "NA"),
	BitDescription(0o134, "NA"),
	BitDescription(0o135, "NA"),
	BitDescription(0o136, "NA"),
	BitDescription(0o137, "NA"),
	
	BitDescription(0o140, "FPOR: BOREN[0] 00 = Brown-out Reset disabled in hardware; SBOREN bit disabled"),
	BitDescription(0o141, "FPOR: BOREN[1] 11 = Brown-out Reset enabled in hardware; SBOREN bit disabled"),
	BitDescription(0o142, "NA"),
	BitDescription(0o143, "FPOR: PWRTEN: 1 = Power-up Timer Enable bit enabled"),
	BitDescription(0o144, "NA"),
	BitDescription(0o145, "FPOR: BORV[0] 00 = Low-power Brown-out Reset occurs around 2.0V"),
	BitDescription(0o146, "FPOR: BORV[1] 11 = Brown-out Reset set to lowest voltage"),
	BitDescription(0o147, "FPOR: MCLRE: 1 = MCLR pin enabled; RA5 input pin disabled"),
	BitDescription(0o150, "NA"),
	BitDescription(0o151, "NA"),
	BitDescription(0o152, "NA"),
	BitDescription(0o153, "NA"),
	BitDescription(0o154, "NA"),
	BitDescription(0o155, "NA"),
	BitDescription(0o156, "NA"),
	BitDescription(0o157, "NA"), 	
	
	BitDescription(0o160, "FICD[0] 10 = PGC2/PGD2 are used for programming the device"),
	BitDescription(0o161, "FICD[1] 00, 11 = Reserved; do not use"),
	BitDescription(0o162, "NA"),
	BitDescription(0o163, "NA"),
	BitDescription(0o164, "NA"),
	BitDescription(0o165, "NA"),
	BitDescription(0o166, "NA"),
	BitDescription(0o167, "NA"),
	BitDescription(0o170, "NA"),
	BitDescription(0o171, "NA"),
	BitDescription(0o172, "NA"),
	BitDescription(0o173, "NA"),
	BitDescription(0o174, "NA"),
	BitDescription(0o175, "NA"),
	BitDescription(0o176, "NA"),
	BitDescription(0o137, "NA"),
)
klx0x_fuseDesc = (
	BitDescription(0o00, "FBS:BWRP 1 = Boot Segment may be written"),
	BitDescription(0o01, "FBS:BSS[0] 001 = High-security Boot Segment starts at 0200h, ends at 15FEh"),
	BitDescription(0o02, "FBS:BSS[1] 101 = Standard security Boot Segment starts at 0200h, ends at 15FEh"),
	BitDescription(0o03, "FBS:BSS[2] 111 = No Boot Segment; all program memory space is General Segment"),
	BitDescription(0o04, "NA"),
	BitDescription(0o05, "NA"),
	BitDescription(0o06, "NA"),
	BitDescription(0o07, "NA"),
	BitDescription(0o10, "NA"),
	BitDescription(0o11, "NA"),
	BitDescription(0o12, "NA"),
	BitDescription(0o13, "NA"),
	BitDescription(0o14, "NA"),
	BitDescription(0o15, "NA"),
	BitDescription(0o16, "NA"),
	BitDescription(0o17, "NA"),
	
	BitDescription(0o20, "NA"),
	BitDescription(0o21, "NA"),
	BitDescription(0o22, "NA"),
	BitDescription(0o23, "NA"),
	BitDescription(0o24, "NA"),
	BitDescription(0o25, "NA"),
	BitDescription(0o26, "NA"),
	BitDescription(0o27, "NA"),
	BitDescription(0o30, "NA"),
	BitDescription(0o31, "NA"),
	BitDescription(0o32, "NA"),
	BitDescription(0o33, "NA"),
	BitDescription(0o34, "NA"),
	BitDescription(0o35, "NA"),
	BitDescription(0o36, "NA"),
	BitDescription(0o37, "NA"),
	
	BitDescription(0o40, "FGS:GWRP: General Segment Code Flash Write Protection bit, 1 = General segment may be written"),
	BitDescription(0o41, "FGS:GSS0 General Segment Code Flash Code Protection bit, 1 = no protection"),
	BitDescription(0o42, "NA"),
	BitDescription(0o43, "NA"),
	BitDescription(0o44, "NA"),
	BitDescription(0o45, "NA"),
	BitDescription(0o46, "NA"),
	BitDescription(0o47, "NA"),
	BitDescription(0o50, "NA"),
	BitDescription(0o51, "NA"),
	BitDescription(0o52, "NA"),
	BitDescription(0o53, "NA"),
	BitDescription(0o54, "NA"),
	BitDescription(0o55, "NA"),
	BitDescription(0o56, "NA"),
	BitDescription(0o57, "NA"),
	
	BitDescription(0o60, "FOSCSEL: FNOSC[0] 101 = 000 = 8 MHz FRC Oscillator (FRC)"),
	BitDescription(0o61, "FOSCSEL: FNOSC[1] 110 = 500 kHz Low-Power FRC oscillator with divide-by-N (LPFRCDIV)"),
	BitDescription(0o62, "FOSCSEL: FNOSC[2] 111 = 8 MHz FRC oscillator with divide-by-N (FRCDIV)"),
	BitDescription(0o63, "NA"),
	BitDescription(0o64, "NA"),
	BitDescription(0o65, "FOSCSEL: SOSCSRC 1 = SOSC analog crystal function is available on the SOSCI/SOSCO pins"),
	BitDescription(0o66, "FOSCSEL: LPRCSEL 1 = High-Power/High-Accuracy mode"),
	BitDescription(0o67, "FOSCSEL: IESO: Internal External Switchover bit, 1 = enabled"),
	BitDescription(0o70, "NA"),
	BitDescription(0o71, "NA"),
	BitDescription(0o72, "NA"),
	BitDescription(0o73, "NA"),
	BitDescription(0o74, "NA"),
	BitDescription(0o75, "NA"),
	BitDescription(0o76, "NA"),
	BitDescription(0o77, "NA"),
	
	BitDescription(0o100, "FOSC: POSCMD[0] 11 = Primary oscillator disabled = HS Oscillator mode selected"),
	BitDescription(0o101, "FOSC: POSCMD[1]"),
	BitDescription(0o102, "FOSC: OSCIOFNC 1 = CLKO output signal active on the OSCO pin"),
	BitDescription(0o103, "FOSC: POSCFREQ[0] 00 = Reserved; do not use"),
	BitDescription(0o104, "FOSC: POSCFREQ[1] 11 = Primary oscillator/external clock input frequency greater than 8 MHz"),
	BitDescription(0o105, "FOSC: SOSCSEL 1 = Secondary oscillator configured for high-power operation"),
	BitDescription(0o106, "FOSC: FCKSM[0] 00 = Clock switching is enabled, Fail-Safe Clock Monitor is enabled"),
	BitDescription(0o107, "FOSC: FCKSM[1] 1x = Clock switching is disabled, Fail-Safe Clock Monitor is disabled"),
	BitDescription(0o110, "NA"),
	BitDescription(0o111, "NA"),
	BitDescription(0o112, "NA"),
	BitDescription(0o113, "NA"),
	BitDescription(0o114, "NA"),
	BitDescription(0o115, "NA"),
	BitDescription(0o116, "NA"),
	BitDescription(0o117, "NA"), 	
    
	BitDescription(0o120, "FWDT: WDTPS[0] 0000 = 1:1"),
	BitDescription(0o121, "FWDT: WDTPS[1] 0001 = 1:2"),
	BitDescription(0o122, "FWDT: WDTPS[2] 0010 = 1:4"),
	BitDescription(0o123, "FWDT: WDTPS[3] 1111 = 1:32768"),
	BitDescription(0o124, "FWDT: FWPSA 1 = WDT prescaler ratio of 1:128"),
	BitDescription(0o125, "FWDT: FWDTEN[0]: 00 = WDT is disabled in hardware; SWDTEN bit is disabled"),
	BitDescription(0o126, "FWDT: WINDIS: 1 = Standard WDT selected; windowed WDT disabled"),
	BitDescription(0o127, "FWDT: FWDTEN[1]: 11 = WDT is enabled in hardware"),
	BitDescription(0o130, "NA"),
	BitDescription(0o131, "NA"),
	BitDescription(0o132, "NA"),
	BitDescription(0o133, "NA"),
	BitDescription(0o134, "NA"),
	BitDescription(0o135, "NA"),
	BitDescription(0o136, "NA"),
	BitDescription(0o137, "NA"),
	
	BitDescription(0o140, "FPOR: BOREN[0] 00 = Brown-out Reset disabled in hardware; SBOREN bit disabled"),
	BitDescription(0o141, "FPOR: BOREN[1] 11 = Brown-out Reset enabled in hardware; SBOREN bit disabled"),
	BitDescription(0o142, "NA"),
	BitDescription(0o143, "FPOR: PWRTEN: 1 = Power-up Timer Enable bit enabled"),
	BitDescription(0o144, "FPOR: I2C1SEL: Alternate MSSP1 I2CTM Pin Mapping bit 1 = default loc."),
	BitDescription(0o145, "FPOR: BORV[0] 00 = Low-power Brown-out Reset occurs around 2.0V"),
	BitDescription(0o146, "FPOR: BORV[1] 11 = Brown-out Reset set to lowest voltage"),
	BitDescription(0o147, "FPOR: MCLRE: 1 = MCLR pin enabled; RA5 input pin disabled"),
	BitDescription(0o150, "NA"),
	BitDescription(0o151, "NA"),
	BitDescription(0o152, "NA"),
	BitDescription(0o153, "NA"),
	BitDescription(0o154, "NA"),
	BitDescription(0o155, "NA"),
	BitDescription(0o156, "NA"),
	BitDescription(0o157, "NA"), 	
	
	BitDescription(0o160, "FICD: ICS[0] 11 = PGEC1/PGED1 are used for programming and debugging the device"),
	BitDescription(0o161, "FICD: ICS[1] 00, 11 = Reserved; do not use"),
	BitDescription(0o162, "NA"),
	BitDescription(0o163, "NA"),
	BitDescription(0o164, "NA"),
	BitDescription(0o165, "NA"),
	BitDescription(0o166, "NA"),
	BitDescription(0o167, "FICD: DEBUG 1 = Background debugger is disabled"),
	BitDescription(0o170, "NA"),
	BitDescription(0o171, "NA"),
	BitDescription(0o172, "NA"),
	BitDescription(0o173, "NA"),
	BitDescription(0o174, "NA"),
	BitDescription(0o175, "NA"),
	BitDescription(0o176, "NA"),
	BitDescription(0o137, "NA"),
)