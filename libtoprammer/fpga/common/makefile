BITGEN		:= bitgen
PAR		:= par
MAP		:= map
NGDBUILD	:= ngdbuild
XST		:= xst

MKDIR		:= mkdir
CP		:= cp
RM		:= rm
LN		:= ln

COMMONDIR	:= ../../common
PART		:= 2s15vq100-5

BITGEN_OPTS	:= -w -g DebugBitstream:No -g Binary:no \
		   -g Gclkdel0:11111 -g Gclkdel1:11111 \
		   -g Gclkdel2:11111 -g Gclkdel3:11111 \
		   -g ConfigRate:4 -g CclkPin:PullUp \
		   -g M0Pin:PullUp -g M1Pin:PullUp -g M2Pin:PullUp \
		   -g ProgPin:PullUp -g DonePin:PullUp \
		   -g TckPin:PullUp -g TdiPin:PullUp \
		   -g TdoPin:PullUp -g TmsPin:PullUp \
		   -g UnusedPin:PullDown -g UserID:0xFFFFFFFF \
		   -g StartUpClk:CClk \
		   -g DONE_cycle:4 -g GTS_cycle:5 \
		   -g GSR_cycle:6 -g GWE_cycle:6 \
		   -g LCK_cycle:NoWait \
		   -g Security:None -g DonePipe:No -g DriveDone:No

XST_OPT_MODE	?= Speed
XST_OPT_LEVEL	?= 2
XST_EXTRA	?=

SRCS		?= $(NAME).v

%.bit: %.ncd
	$(BITGEN) $(BITGEN_OPTS) $< $@

%.ncd: %_map.ncd
	$(PAR) -w -ol std -t 1 $< $@ `basename $@ .ncd`.pcf

%_map.ncd: %.ngd
	$(MAP) -p $(PART) -cm area -pr b -k 4 -c 100 -o $@ \
		$< `basename $< .ngd`.pcf

%.ngd: %.ngc %.ucf
	$(NGDBUILD) -aul -dd __ngo -uc `basename $@ .ngd`.ucf \
		-p $(PART) $< $@

%.ngc: %.xst %.lso %.prj $(SRCS)
	$(MKDIR) -p __xst/tmp
	$(XST) -ifn $<

%.ucf:
	[ -f '$@' ] || $(LN) -s '$(COMMONDIR)/common.ucf' '$@'

%.lso:
	echo 'work' > '$@'

%.prj:
	echo 'verilog work "$(SRCS)"' > '$@'

%.xst:
	$(CP) '$(COMMONDIR)/common.xst' '$@'
	echo '-ifn $(NAME).prj' >> '$@'
	echo '-ofn $(NAME)' >> '$@'
	echo '-lso $(NAME).lso' >> '$@'
	echo "-top `echo -n '$(NAME)' | tr - _`" >> '$@'
	echo '-opt_mode $(XST_OPT_MODE)' >> '$@'
	echo '-opt_level $(XST_OPT_LEVEL)' >> '$@'
	[ -n '$(XST_EXTRA)' ] && echo '$(XST_EXTRA)' >> '$@' || true

all: $(NAME).bit

clean:
	$(RM) -rf __ngo __xst *.bgn *.bit *.bld *.drc *_map.mrp \
		*_map.ncd *_map.ngm *.ncd *.ngc *.ngd *.ngr \
		*.pad *_pad.csv *_pad.txt *.par *.pcf *.srp \
		*.unroutes *_usage.xml *.xpi *_map.map *_summary.xml \
		*.twr *_details.xml *.ptwx *.xrpt xlnx_auto_* \
		*.lso *.prj *.xst
	[ -h '$(NAME).ucf' ] && $(RM) -f '$(NAME).ucf' || true

.PHONY: all clean
