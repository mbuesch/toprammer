import hc4094sniffer
import time

def sniff(hw, nrChips, xor, mask, shift, format, nrInLine, action):
	hw.loadGNDLayout(0)
	hw.loadVCCLayout(0)
	hw.loadVPPLayout(0)
	hw.setVCCVoltage(5)
	hw.setVPPVoltage(5)
	hw.flushCommands()
	s = hc4094sniffer.Sniffer("/dev/ttyUSB0", nrChips)
	count = offs = 0
	for index in range(0x100):
		s.clear()
		action(0)
		action(index)
		hw.flushCommands()
		time.sleep(0.1)
		buf = s.read()
		d = 0
		for i in range(nrChips):
			d |= buf[i] << (8 * i)
		d ^= xor
		d &= mask
		d >>= shift
		print(format % d, end='')
		count += 1
		if count == nrInLine:
			print(" # 0x%02X" % offs)
			count = 0
			offs += nrInLine
		else:
			print(" ", end='')

def sniffGNDLayouts(hw):
	sniff(hw, nrChips=2,
	      xor=0x3FE0, mask=0xC000, shift=0,
	      format="0x%04X,",
	      nrInLine=8,
	      action=lambda layout: hw.loadGNDLayout(layout))

def sniffVCCLayouts(hw):
	sniff(hw, nrChips=2,
	      xor=0x3FE0, mask=0x3F00, shift=0,
	      format="0x%04X,",
	      nrInLine=8,
	      action=lambda layout: hw.loadVCCLayout(layout))

def sniffVPPLayouts(hw):
	sniff(hw, nrChips=2,
	      xor=0xFFFF, mask=0xFF9F, shift=0,
	      format="0x%04X,",
	      nrInLine=8,
	      action=lambda layout: hw.loadVPPLayout(layout))

def sniffVPPVoltages(hw):
	sniff(hw, nrChips=2,
	      xor=0x3FE0, mask=0x001F, shift=0,
	      format="0x%04X,",
	      nrInLine=8,
	      action=lambda centivolts: hw.setVPPVoltage(centivolts / 10.0))
