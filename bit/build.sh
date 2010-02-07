#!/bin/bash
# Rebuild all FPGA bit files

srcdir="./src"
bindir="."

for src in $srcdir/*; do
	[ -d "$src" ] || continue

	srcname="$(basename $src)"
	logfile="$bindir/$srcname.build.log"

	echo "Building $srcname..."
	make -C $src/ clean >/dev/null
	if [ $? -ne 0 ]; then
		echo "FAILED to clean $srcname."
		exit 1
	fi
	make -C $src/ all >$logfile
	if [ $? -ne 0 ]; then
		cat $logfile
		echo "FAILED to build $srcname."
		exit 1
	fi
	cat $logfile | grep WARNING
	cp -f $src/$srcname.bit $bindir/$srcname.bit
	make -C $src/ clean >/dev/null
	if [ $? -ne 0 ]; then
		echo "FAILED to clean $srcname."
		exit 1
	fi
	rm -f $logfile
done
echo "Successfully built all images."

exit 0
