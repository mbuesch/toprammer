#!/usr/bin/env python3

"""
#    TOP2049 Open Source programming suite
#
#    Commandline utility
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

import re
import sys
import os

def substitute(input, oldSocket, newSocket):
	input = re.sub('(^\s*packages).*', lambda m:'{} = (("DIP10", ""), ),'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPackage).*', lambda m:'{} = "DIP10",'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPinVCC).*', lambda m:'{} = 9,'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPinsVPP).*', lambda m:'{} = 10,'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPinGND).*', lambda m:'{} = 8,'.format(m.group(1)), input)
	input = re.sub('(^\s*runtimeID).*', lambda m:'{} = (0xDF05, 0x01),'.format(m.group(1)), input)
	input = re.sub('(^\s*description).+"(.*)".*', lambda m:'{} = "{} - ICD",'.format(m.group(1), m.group(2)), input)
	input = re.sub('(^\s*bitfile).*', lambda m:'{} = "microchip16sip6",'.format(m.group(1)), input)
	input = re.sub("{}".format(oldSocket), "{}".format(newSocket), input)
	input = re.sub("{}".format(oldSocket.upper()), "{}".format(newSocket.upper()), input)
	return input

def makeSip():
	inputFileName = '__init__.py'
	fin = open(inputFileName)
	dMCU = {}
	for line in fin:
		matchObj = re.match('.*(pic[0-9]+l?f\w+)(sip[0-9a]+).*', line)
		if matchObj:
			continue
		matchObj = re.match('.*(pic[0-9]+l?f\w+)(dip[0-9a]+).*', line)
		if not matchObj:
			print("{} did not match".format(line))
			continue
#		print('matched {} - {}'.format(matchObj.group(1), matchObj.group(2)))
		dMCU.setdefault(matchObj.group(1), matchObj.group(2))
	fin.close()
	for item in dMCU.items():
		fin = open("{}{}.py".format(item[0], item[1]))
		fout = open("{}sip6.py".format(item[0]), 'w')
		fout.write("#\n")
		fout.write("# THIS FILE WAS AUTOGENERATED BY makeSip6.py\n")
		fout.write("# Do not edit this file manually. All changes will be lost.\n")
		fout.write("#\n\n")
		for line in fin:
			fout.write(substitute(line, "{}".format(item[1]), "sip6"))
		fout.close()
		fin.close()

def main(argv):
	makeSip()

if __name__ == "__main__":
	exit(main(sys.argv))
