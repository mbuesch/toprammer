/*
 *   TOP2049 Open Source programming suite
 *
 *   Atmel AT89S5X DIP40
 *   FPGA bottomhalf implementation
 *
 *   Copyright (c) 2010 Guido
 *   Copyright (c) 2010 Michael Buesch <m@bues.ch>
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

/* The runtime ID and revision. */
`define RUNTIME_ID	16'h0005
`define RUNTIME_REV	16'h01

module at89s5xdip40(data, ale, write, read, osc_in, zif);
	inout [7:0] data;
	input ale;
	input write;
	input read;
	input osc_in; /* 24MHz oscillator */
	inout [48:1] zif;

	/* Interface to the microcontroller */
	wire read_oe;		/* Read output-enable */
	reg [7:0] address;	/* Cached address value */
	reg [7:0] read_data;	/* Cached read data */

	wire low, high;		/* Constant lo/hi */

	/* Programmer context */
	reg [1:0] prog_busy;
	reg [3:0] prog_command;
	reg [3:0] prog_state;
	reg [3:0] prog_count;
	reg prog_err;

	/* DUT signals */
	reg [7:0] dut_data;
	reg [13:0] dut_addr;
	reg dut_p26;
	reg dut_p27;
	reg dut_p33;
	reg dut_p36;
	reg dut_p37;
	reg dut_psen;
	reg dut_prog;
	reg dut_vpp;
	reg dut_rst;
	wire dut_clock;


	assign low = 0;
	assign high = 1;

	initial begin
		prog_busy <= 0;
		prog_command <= 0;
		prog_state <= 0;
		prog_err <= 0;
		prog_count <= 0;
		dut_data <= 0;
		dut_addr <= 0;
		dut_p26 <= 0;
		dut_p27 <= 0;
		dut_p33 <= 0;
		dut_p36 <= 0;
		dut_p37 <= 0;
		dut_psen <= 0;
		dut_prog <= 0;
		dut_vpp <= 0;
		dut_rst <= 0;
	end

	/* The delay counter. Based on the 24MHz input clock. */
	reg [15:0] delay_count;
	wire osc;
	assign dut_clock=osc;
	IBUF osc_ibuf(.I(osc_in), .O(osc));

	always @(posedge osc) begin
		if (delay_count == 0) begin
			if (prog_busy[0] != prog_busy[1]) begin
				/* busy0 != busy1 indicates that a command is running.
				* Continue executing it... */
				case (prog_command)
				1: begin /* Set P3.2 after init */
					dut_prog <= 1;
					prog_busy[1] <= prog_busy[0];
				end
				2: begin /* clear P3.2 before shutdown */
					dut_prog <= 0;
					prog_busy[1] <= prog_busy[0];
				end
				3: begin /* do nPROG pulsep with wait for ready */
					case (prog_state)
					0: begin /* raise dut_prog */
                        dut_prog <= 1;
                        prog_state <= 1;
                        delay_count <= 48;/*2us (48 tcl) wait*/
                        prog_err <= 0;
                    end
					1: begin /* pulse */
						delay_count <= 24;/* each 1us  */
						dut_prog <= 0;
						prog_state <= 2;
					end
					2: begin /* raise dut_prog */
						dut_prog <= 1;
						prog_state <= 3;
						prog_count <= 12;
						delay_count <= 48;/*2us (48 tcl) wait*/
					end
					3: begin /* wait for ready (zif[14]) == 1 */
						if (zif[14] == 0) begin
							delay_count <= 80; /* each 3330ns	 */
							prog_count <= prog_count - 1;
							if (prog_count == 0) begin
								prog_err <= 1;
								prog_state <= 4;
							end
						end
						else begin
							prog_state <= 4;
						end
					end
					4: begin /* finish */
						prog_state <= 0;
						prog_busy[1] <= prog_busy[0];
					end
					endcase
				end
				4: begin /* do nPROG pulsep */
					case (prog_state)
					0: begin
                        dut_prog <= 1;
                        prog_state <= 1;
                        delay_count <= 48;/*48tcy, 2us*/
                        prog_err <= 0;
                    end
					1: begin /* pulse */
						delay_count <= 24; /* 1us each */
						dut_prog <= 0;
						prog_state <= 2;
					end
					2: begin
						dut_prog <= 1;
						prog_state <= 3;
						delay_count <= 48;/*48tcy, 2us*/
					end
                    3: begin
                        prog_busy[1] <= prog_busy[0];
                        prog_state <= 0;
                    end					
					endcase
				end
				5: begin /* set dut_vpp */
					dut_vpp <= 1;
					prog_busy[1] <= prog_busy[0];
				end
				6: begin /* clear dut_vpp */
					dut_vpp <= 0;
					prog_busy[1] <= prog_busy[0];
				end
				endcase
			end
		end else begin
			delay_count <= delay_count - 1;
		end
	end

	always @(posedge write) begin
		case (address)
		8'h10: begin
			/* Data write */
			dut_data <= data;
		end
        8'h11: begin
            /* Address LSB write */
            dut_addr[7:0] <= data;
        end
        8'h12: begin
            /* Address MSB write */
            dut_addr[13:8] <= data[5:0];
        end
		8'h13: begin
			/* Run a command. */
			prog_command <= data;
			prog_busy[0] <= ~prog_busy[1];
		end
		8'h16: begin
			/* Set P26, P27, P33, P36, P37, dut_psen, dut_rst */
			dut_p26 <= data[0];
			dut_p27 <= data[1];
			dut_p33 <= data[2];
			dut_p36 <= data[3];
			dut_p37 <= data[4];
			dut_psen <= data[5];
			dut_rst <= data[6];
		end
		endcase
	end

	always @(negedge read) begin
		case (address)
		8'h10: begin
			/* Data read */
			read_data[7] <= zif[36];
			read_data[6] <= zif[37];
			read_data[5] <= zif[38];
			read_data[4] <= zif[39];
			read_data[3] <= zif[40];
			read_data[2] <= zif[41];
			read_data[1] <= zif[42];
			read_data[0] <= zif[43];
		end
		8'h12: begin
			/* Read status */
			read_data[0] <= (prog_busy[0] != prog_busy[1]);
			read_data[1] <= prog_err;
		end

		8'hFD: read_data <= `RUNTIME_ID & 16'hFF;
		8'hFE: read_data <= (`RUNTIME_ID >> 8) & 16'hFF;
		8'hFF: read_data <= `RUNTIME_REV;
		endcase
	end

	always @(negedge ale) begin
		address <= data;
	end

	assign read_oe = !read && address[4];

	bufif0(zif[1], low, low);
	bufif0(zif[2], low, low);
	bufif0(zif[3], low, low);
	bufif0(zif[4], low, low);
	









	bufif0(zif[5], dut_addr[0], dut_p26);
	bufif0(zif[6], dut_addr[1], dut_p26);
	bufif0(zif[7], dut_addr[2], dut_p26);
	bufif0(zif[8], dut_addr[3], dut_p26);
	bufif0(zif[9], dut_addr[4], dut_p26);
	bufif0(zif[10], dut_addr[5], dut_p26);
	bufif0(zif[11], dut_addr[6], dut_p26);
	bufif0(zif[12], dut_addr[7], dut_p26);
	bufif0(zif[13], dut_rst, low); /*Reset*/
	bufif0(zif[14], low, high); /* P3.0 */
	bufif0(zif[15], low, low); /* P3.1 */
	bufif0(zif[16], low, low); /* P3.2 */		
	bufif0(zif[17], dut_p33, low); /* P3.3 */
	bufif0(zif[18], low, low); /* P3.4 */
	bufif0(zif[19], low, low); /* P3.5 */
	bufif0(zif[20], dut_p36, low); /* P3.6 */
	bufif0(zif[21], dut_p37, low); /* P3.7 */
	bufif0(zif[22], low, high); 		/* XTAL2 */
	bufif0(zif[23], dut_clock, low);		/* XTAL1 */
    bufif0(zif[24], low, low); /* GND */









	
	bufif0(zif[25], dut_addr[8], dut_p26); /* P2.0 */
	bufif0(zif[26], dut_addr[9], dut_p26); /* P2.1 */
	bufif0(zif[27], dut_addr[10], dut_p26); /* P2.2 */
	bufif0(zif[28], dut_addr[11], dut_p26); /* P2.3 */
	bufif0(zif[29], dut_addr[12], dut_p26); /* P2.4 */
	bufif0(zif[30], dut_addr[13], dut_p26); /* P2.5 */
	bufif0(zif[31], dut_p26, low);	/* P2.6 */
	bufif0(zif[32], dut_p27, low);	/* P2.7 */
	bufif0(zif[33], dut_psen, low);	/* !PSEN */
	bufif0(zif[34], dut_prog, low);	/* !PROG */
	bufif0(zif[35], low, dut_vpp);       /* VPP/Reset */
	bufif0(zif[36], dut_data[7], !(!dut_p26 && dut_p27));
	bufif0(zif[37], dut_data[6], !(!dut_p26 && dut_p27));
	bufif0(zif[38], dut_data[5], !(!dut_p26 && dut_p27));
	bufif0(zif[39], dut_data[4], !(!dut_p26 && dut_p27));
	bufif0(zif[40], dut_data[3], !(!dut_p26 && dut_p27));
	bufif0(zif[41], dut_data[2], !(!dut_p26 && dut_p27));
	bufif0(zif[42], dut_data[1], !(!dut_p26 && dut_p27));
	bufif0(zif[43], dut_data[0], !(!dut_p26 && dut_p27));
	bufif0(zif[44], high, low);        /* VCC */

	bufif0(zif[45], low, low);
	bufif0(zif[46], low, low);
	bufif0(zif[47], low, low);
	bufif0(zif[48], low, low);

	bufif1(data[0], read_data[0], read_oe);
	bufif1(data[1], read_data[1], read_oe);
	bufif1(data[2], read_data[2], read_oe);
	bufif1(data[3], read_data[3], read_oe);
	bufif1(data[4], read_data[4], read_oe);
	bufif1(data[5], read_data[5], read_oe);
	bufif1(data[6], read_data[6], read_oe);
	bufif1(data[7], read_data[7], read_oe);
endmodule
