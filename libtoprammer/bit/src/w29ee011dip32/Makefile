BITGEN		= bitgen
PAR		= par
MAP		= map
NGDBUILD	= ngdbuild
XST		= xst
MKDIR		= mkdir

PART		= 2s15vq100-5
NAME		= w29ee011dip32
SRCS		= $(NAME).v

%.bit: %.ncd
	$(BITGEN) -f `basename $< .ncd`.ut $<

%.ncd: %_map.ncd
	$(PAR) -w -ol std -t 1 $< $@ `basename $< _map.ncd`.pcf

%_map.ncd: %.ngd
	$(MAP) -p $(PART) -cm area -pr b -k 4 -c 100 -o `basename $< .ngd`_map.ncd $< `basename $< .ngd`.pcf

%.ngd: %.ngc
	$(NGDBUILD) -aul -dd __ngo -uc `basename $< .ngc`.ucf -p $(PART) $< $@

%.ngc: %.xst $(SRCS)
	$(MKDIR) -p __xst/tmp
	$(XST) -ifn $<

all: $(NAME).bit

clean:
	rm -Rf __ngo __xst *.bgn *.bit *.bld *.drc *_map.mrp \
		*_map.ncd *_map.ngm *.ncd *.ngc *.ngd *.ngr \
		*.pad *_pad.csv *_pad.txt *.par *.pcf *.srp \
		*.unroutes *_usage.xml *.xpi *_map.map *_summary.xml \
		*.twr *_details.xml


