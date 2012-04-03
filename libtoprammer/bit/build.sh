#!/bin/bash
# Rebuild FPGA bit files
# Copyright (c) 2010 Michael Buesch <m@bues.ch>
# Licensed under the GNU/GPL v2+

basedir="$(dirname "$0")"
[ "${basedir:0:1}" = "/" ] || basedir="$PWD/$basedir"

srcdir="$basedir/src"
bindir="$basedir"
bitparser="python $basedir/../bitfile.py"

function die
{
	echo "$*" >&2
	exit 1
}

function terminate
{
	die "Interrupted."
}

trap terminate TERM INT

function usage
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
nr_targets=0
while [ $# -gt 0 ]; do
	if [ "$1" = "-h" -o "$1" = "--help" ]; then
		usage
		exit 0
	fi
	if [ "$1" = "-v" -o "$1" = "--verbose" ]; then
		verbose=1
		shift
		continue
	fi
	target="$1"
	target="${target%.bit}"	# strip .bit suffix
	targets[nr_targets]="$target"
	let nr_targets=nr_targets+1
	shift
done

function bitparser
{
	python "$basedir/../bitfile.py" "$@" || die "Failed to execute bitparser"
}

function should_build # $1=target
{
	target="$1"
	[ "$target" = "template" ] && return 1
	[ $nr_targets -eq 0 ] && return 0
	let end=nr_targets-1
	for i in $(seq 0 $end); do
		[ ${targets[i]} = "$target" ] && return 0
	done
	return 1
}

# Check if the payload of two bitfiles matches
function bitfile_is_equal # $1=file1, $2=file2
{
	[ -r $1 -a -r $2 ] || return 1
	bitparser "$1" NOACTION # Test if bitparser works
	sum1="$(bitparser "$1" GETPAYLOAD | sha1sum - | cut -d' ' -f1)"
	sum2="$(bitparser "$2" GETPAYLOAD | sha1sum - | cut -d' ' -f1)"
	[ "$sum1" = "$sum2" ]
}

for src in $srcdir/*; do
	[ -d "$src" ] || continue

	srcname="$(basename $src)"
	logfile="$bindir/$srcname.build.log"

	should_build $srcname || continue

	echo "Building $srcname..."
	make -C $src/ clean >/dev/null
	if [ $? -ne 0 ]; then
		echo "FAILED to clean $srcname."
		exit 1
	fi
	if [ $verbose -eq 0 ]; then
		make -C $src/ all >$logfile
		if [ $? -ne 0 ]; then
			cat $logfile
			echo "FAILED to build $srcname."
			exit 1
		fi
		cat $logfile | grep WARNING
	else
		make -C $src/ all
		if [ $? -ne 0 ]; then
			echo "FAILED to build $srcname."
			exit 1
		fi
	fi

	new="$src/$srcname.bit"
	old="$bindir/$srcname.bit"
	if bitfile_is_equal "$old" "$new"; then
		echo "Bitfile for target $srcname did not change"
	else
		cp -f "$new" "$old"
	fi
	make -C $src/ clean >/dev/null
	if [ $? -ne 0 ]; then
		echo "FAILED to clean $srcname."
		exit 1
	fi
	rm -f $logfile
done
echo "Successfully built all images."

exit 0
