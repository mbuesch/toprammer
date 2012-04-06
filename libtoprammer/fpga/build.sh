#!/bin/sh
# Rebuild FPGA bit files
# Copyright (c) 2010-2012 Michael Buesch <m@bues.ch>
# Licensed under the GNU/GPL v2+

basedir="$(dirname "$0")"
[ "$(echo -n "$basedir" | cut -c1)" = "/" ] || basedir="$PWD/$basedir"

srcdir="$basedir/src"
bindir="$basedir"


die()
{
	echo "$*" >&2
	exit 1
}

terminate()
{
	die "Interrupted."
}

trap terminate TERM INT

usage()
{
	echo "Usage: build.sh [OPTIONS] [TARGETS]"
	echo
	echo "Options:"
	echo " -h|--help           Show this help text"
	echo " -v|--verbose        Verbose build"
	echo
	echo "Targets:"
	echo "Specify the names of the targets to build, or leave blank to rebuild all."
}

# Parse commandline
verbose=0
targets="/"
while [ $# -gt 0 ]; do
	[ "$1" = "-h" -o "$1" = "--help" ] && {
		usage
		exit 0
	}
	[ "$1" = "-v" -o "$1" = "--verbose" ] && {
		verbose=1
		shift
		continue
	}
	target="$1"
	target="${target%.bit}"	# strip .bit suffix
	# Add to list
	targets="${targets}${target}/"
	shift
done
[ "$targets" = "/" ] && targets=

bitparser()
{
	python "$basedir/../bitfile.py" "$@" ||\
		die "Failed to execute bitparser"
}

should_build() # $1=target
{
	target="$1"
	[ "$target" = "template" ] && return 1
	[ -z "$targets" ] && return 0
	echo "$targets" | grep -qe '/'"$target"'/'
}

# Check if the payload of two bitfiles matches
bitfile_is_equal() # $1=file1, $2=file2
{
	[ -r $1 -a -r $2 ] || return 1
	bitparser "$1" NOACTION # Test if bitparser works
	sum1="$(bitparser "$1" GETPAYLOAD | sha1sum -b - | awk '{print $1;}')"
	sum2="$(bitparser "$2" GETPAYLOAD | sha1sum -b - | awk '{print $1;}')"
	[ "$sum1" = "$sum2" ]
}

for src in $srcdir/*; do
	[ -d "$src" ] || continue

	srcname="$(basename $src)"
	logfile="$bindir/$srcname.build.log"

	should_build $srcname || continue

	echo "Building $srcname..."
	make -C $src/ clean >/dev/null ||\
		die "FAILED to clean $srcname."
	if [ $verbose -eq 0 ]; then
		make -C $src/ all >$logfile || {
			cat $logfile
			die "FAILED to build $srcname."
		}
		cat $logfile | grep WARNING
	else
		make -C $src/ all ||\
			die "FAILED to build $srcname."
	fi

	new="$src/$srcname.bit"
	old="$bindir/$srcname.bit"
	if bitfile_is_equal "$old" "$new"; then
		echo "Bitfile for target $srcname did not change"
	else
		cp -f "$new" "$old"
	fi
	make -C $src/ clean >/dev/null ||\
		die "FAILED to clean $srcname."
	rm -f $logfile
done
echo "Successfully built all images."

exit 0
