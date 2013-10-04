#!/usr/bin/env python

"""
#    TOP2049 Open Source programming suite
#
#    Commandline utility
#
#    Copyright (c) 2013 Pavel Stemberk <stemberk@gmail.com>
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

def clear():
	inputFileName = '__init__.py'
	tmpFileName = 'tmp'
	fin = open(inputFileName)
	ftmp = open(tmpFileName, 'w')
	isToBeRemoved = False
	for line in fin:
		if isToBeRemoved:
			matchObj = re.match('.*(pic\w+).*', line)
			if matchObj:
				print('removing file {}'.format(matchObj.group(1)))
				os.remove('{}.py'.format(matchObj.group(1)))
		else:
			ftmp.write(line)
			matchObj = re.match('#do not edit the text below this line.*', line)
			if matchObj:
				isToBeRemoved = True
	fin.close()
	ftmp.close()
	os.rename(tmpFileName, inputFileName)
    
def substitute(input, oldSocket, newSocket):
	input = re.sub('(^\s*packages).*', lambda m:'{} = (("DIP10", ""), ),'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPackage).*', lambda m:'{} = "DIP10",'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPinVCC).*', lambda m:'{} = 9,'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPinsVPP).*', lambda m:'{} = 10,'.format(m.group(1)), input)
	input = re.sub('(^\s*chipPinGND).*', lambda m:'{} = 8,'.format(m.group(1)), input)
	input = re.sub('(^\s*runtimeID).*', lambda m:'{} = (0xDE05, 0x01),'.format(m.group(1)), input)
	input = re.sub('(^\s*description).+"(.*)".*', lambda m:'{} = "{} - ICD",'.format(m.group(1), m.group(2)), input)
	input = re.sub('(^\s*bitfile).*', lambda m:'{} = "microchip01sip6",'.format(m.group(1)), input)
	input = re.sub("{}".format(oldSocket), "{}".format(newSocket), input)
	return input
    
    
def makeSip():
	inputFileName = '__init__.py'
	fin = open(inputFileName)
	# from pic16f1824dip14 import *
	dMCU = {}
	for line in fin:
		matchObj = re.match('#do not edit the text below this line.*', line)
		if matchObj:
			break
		matchObj = re.match('.*(pic[0-9]+l?f\w+)(dip[0-9a]+).*', line)
		print('matched {} - {}'.format(matchObj.group(1), matchObj.group(2)))
		dMCU.setdefault(matchObj.group(1), matchObj.group(2))
	fin.close()
	finit = open("init", "a")
	for item in dMCU.items():
		fin = open("{}{}.py".format(item[0], item[1]))
		fout = open("{}sip6.py".format(item[0]), 'w')
		for line in fin:
			fout.write(substitute(line, "{}".format(item[1]), "sip6"))
		fout.close()
		fin.close()
		finit.write("from {}sip6 import *\n".format(item[0]))
	finit.close()
	print ('{} - {}'.format(item[0], item[1]))	
	
def main(argv):
	clear()
	# makeSip()

if __name__ == "__main__":
	xit(main(sys.argv))
