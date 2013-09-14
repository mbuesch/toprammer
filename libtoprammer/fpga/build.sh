#!/bin/sh
# Rebuild FPGA bit files
# Copyright (c) 2010-2012 Michael Buesch <m@bues.ch>
# Licensed under the GNU/GPL v2+

basedir="$(dirname "$0")"
[ "$(echo -n "$basedir" | cut -c1)" = "/" ] || basedir="$PWD/$basedir"

srcdir="$basedir/src"
bindir="$basedir/bin"


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
	target="$(basename "$1" .bit)"
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

# $1=src-directory, $1=verbose
warning_filter()
{
	local chip_filter="$1/warning.filter"
	local global_filter="$basedir/warning.filter"
	local verbose="$2"

	[ -n "$verbose" -a "$verbose" != "0" ] && {
		# Show all messages
		cat
		return 0
	}

	# Read filter regexes
	local discard_regexes=
	[ -r "$global_filter" ] &&\
		discard_regexes="$discard_regexes $(cat "$global_filter")"
	[ -r "$chip_filter" ] &&\
		discard_regexes="$discard_regexes $(cat "$chip_filter")"

	# Filter for warnings and remove blacklisted warnings.
	grep -Ee '^WARNING' | while read line; do
		local discard=
		for discard_regex in $discard_regexes; do
			echo "$line" | grep -Eqe "$discard_regex" && {
				discard=1  # Discard it!
				break
			}
		done
		[ -z "$discard" ] && echo "$line"
	done
}

# $1=source_directory
run_build()
{
	local source_dir="$1"

	for src in "$source_dir"/*; do
		[ -d "$src" ] || continue

		[ -f "$src/Makefile" ] || {
			# Recurse
			run_build "$src"
			continue
		}

		srcname="$(basename $src)"
		logfile="$basedir/$srcname.build.log"

		should_build "$srcname" || continue

		echo "Building $srcname..."
		rm -f "$logfile"
		make -C "$src/" clean >/dev/null ||\
			die "FAILED to clean $srcname."
		errfile="$(mktemp)"
		{
			make -C "$src/" all 2>&1
			echo "$?" >> "$errfile"
		} | tee "$logfile" | warning_filter "$src" "$verbose"
		errcode="$(cat "$errfile")"
		rm -f "$errfile"
		[ "$errcode" = "0" ] || {
			[ $verbose -eq 0 ] && cat "$logfile"
			die "FAILED to build $srcname."
		}

		new="$src/$srcname.bit"
		old="$bindir/$srcname.bit"
		if bitfile_is_equal "$old" "$new"; then
			echo "Bitfile for target $srcname did not change"
		else
			cp -f "$new" "$old"
		fi
		make -C "$src/" clean > /dev/null ||\
			die "FAILED to clean $srcname."
		rm -f "$logfile"
	done
}

# Pull in the ISE settings and paths.
if [ -d "$XILINX_10_1_DIR" ] && \
   [ -r "$XILINX_10_1_DIR/ISE/settings32.sh" ]; then
	. "$XILINX_10_1_DIR/ISE/settings32.sh"
elif [ -r "/opt/Xilinx/10.1/ISE/settings32.sh" ]; then
	. "/opt/Xilinx/10.1/ISE/settings32.sh"
else
	die "Did not find Xilinx ISE webpack 10.1"
fi

run_build "$srcdir"
echo "Successfully built all images."

exit 0
