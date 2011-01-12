#!/bin/bash
# Toprammer regression tests
# Copyright (c) 2010 Michael Buesch <mb@bu3sch.de>

basedir="$(dirname "$0")"
[ "${basedir:0:1}" = "/" ] || basedir="$PWD/$basedir"

tmpdir="/tmp/toprammer-test-$$"


cleanup_enabled=1

function cleanup
{
	[ $cleanup_enabled -ne 0 ] || return
	echo "Cleanup..."
	rm -Rf "$tmpdir"
}

trap cleanup INT TERM

function info
{
	echo "$current_test:  $@"
}

function warning
{
	echo "WARNING $current_test:  $@"
}

function error
{
	echo "ERROR $current_test:  $@"
}

function abort
{
	cleanup
	exit 1
}

function die
{
	error $@
	cleanup
	exit 1
}

function toprammer
{
	local args="$@"
	local logfile="$tmpdir/toprammer.log"

	echo "        toprammer $args"
	cd "$basedir/.." || die "Failed to chdir"
	if [ $verbose -eq 0 ]; then
		./toprammer $args >$logfile 2>&1
		if [ $? -ne 0 ]; then
			[ -r "$logfile" ] && cat "$logfile"
			die "toprammer $args  <<<FAILED>>>"
		fi
	else
		./toprammer $args -V2
		[ $? -eq 0 ] || die "toprammer $args  <<<FAILED>>>"
	fi
}

function toprammer_layout_silent
{
	local args="$@"
	local logfile="$tmpdir/toprammer-layout.log"
	echo "        toprammer-layout $args"
	cd "$basedir/.." || die "Failed to chdir"
	./toprammer-layout $args >$logfile 2>&1
	if [ $? -ne 0 ]; then
		[ -r "$logfile" ] && cat "$logfile"
		die "toprammer-layout $args  <<<FAILED>>>"
	fi
}

function toprammer_layout
{
	local args="$@"
	cd "$basedir/.." || die "Failed to chdir"
	./toprammer-layout $args
	[ $? -eq 0 ] || die "toprammer-layout $args  <<<FAILED>>>"
}

function ask
{
	read -n1 -p "$@ " ok
	echo
	[ "$ok" = "y" -o "$ok" = "Y" -o \
	  "$ok" = "1" -o "$ok" = "" ] && return 0
	return 1
}

function request
{
	read -s -n1 -p "$@" res
	echo
	[ "$res" = "a" ] && abort
	[ "$res" = "x" ] && return 1
	return 0
}

function request_DUT # $1=DUT-name
{
	local dut="$1"
	toprammer_layout -d "$current_device" -p "$dut" --only-insert
	request "Please insert a $dut into the ZIF socket (x to skip; a to abort)..."
}

function request_TOP # $1=TOPxxxx
{
	request "Please connect the $@ programmer (x to skip; a to abort)..."
}

function create_random_file # $1=file $2=bs $3=count
{
	dd if=/dev/urandom of="$1" bs="$2" count="$3" >/dev/null 2>&1
	[ $? -eq 0 ] || die "Failed to create $1"
	chmod 444 "$1"
	[ $? -eq 0 ] || die "Failed to set $1 read-only"
}

function compare_files # $1=file1 $2=file2
{
	[ -r "$1" -a -r "$2" ] || return 1
	sum1="$(sha1sum "$1" | cut -d' ' -f1)"
	sum2="$(sha1sum "$2" | cut -d' ' -f1)"
	[ "$sum1" = "$sum2" ]
}

function compare_file_to_hex # $1=file $2=hex_string
{
	local filehex="$(hexdump -v -e '/1 "%02X"' $1)"
	[ "$filehex" = "$2" ]
}

function usage
{
	echo "Usage: run-tests.sh <OPTIONS> <SCRIPTPATH>"
	echo
	echo "Options:"
	echo " -h|--help               Show this help text"
	echo " -V|--verbose            Be verbose"
	echo
	echo "If the optional scriptpath is specified, only that testscript"
	echo "is executed. The scriptpath is DEVICE/TESTSCRIPT. Example:"
	echo "   top2049/001-atmega32dip40.test"
	echo "This will execute the atmega32 test for the TOP2049 and exit."
	echo "If no path is specified, all tests will be executed."
}

# Parse commandline
nr_scriptpaths=0
verbose=0
while [ $# -gt 0 ]; do
	if [ "$1" = "-h" -o "$1" = "--help" ]; then
		usage
		exit 0
	fi
	if [ "$1" = "-V" -o "$1" = "--verbose" ]; then
		verbose=1
		shift
		continue
	fi
	scriptpaths[nr_scriptpaths]="$1"
	let nr_scriptpaths=nr_scriptpaths+1
	shift
done

current_test=
current_device=
cleanup
mkdir -p "$tmpdir"
[ $? -eq 0 ] || die "Failed to create $tmpdir"

# Create various test files
tmpfile="$tmpdir/tmpfile"

testfile_64="$tmpdir/testfile_64"
create_random_file "$testfile_64" 64 1

testfile_128="$tmpdir/testfile_128"
create_random_file "$testfile_128" 128 1

testfile_256="$tmpdir/testfile_256"
create_random_file "$testfile_256" 256 1

testfile_512="$tmpdir/testfile_512"
create_random_file "$testfile_512" 512 1

testfile_1k="$tmpdir/testfile_1k"
create_random_file "$testfile_1k" 1024 1

testfile_2k="$tmpdir/testfile_2k"
create_random_file "$testfile_2k" 1024 2

testfile_4k="$tmpdir/testfile_4k"
create_random_file "$testfile_4k" 4096 1

testfile_8k="$tmpdir/testfile_8k"
create_random_file "$testfile_8k" 4096 2

testfile_16k="$tmpdir/testfile_16k"
create_random_file "$testfile_16k" 4096 4

testfile_32k="$tmpdir/testfile_32k"
create_random_file "$testfile_32k" 4096 8

testfile_128k="$tmpdir/testfile_128k"
create_random_file "$testfile_128k" 4096 32


function do_run_test # $1=device, $2=testscript
{
	current_device="$1"
	current_test="$1/$2"

	echo "Running $current_test..."
	rm -f "$tmpfile"

	# Import the testscript
	. "$basedir/defaults.test"
	. "$basedir/$current_test"

	# And run the tests
	while $(true); do
		test_init
		[ $? -eq 0 ] || break
		cleanup_enabled=0
		( test_run )
		local res=$?
		cleanup_enabled=1
		if [ $res -ne 0 ]; then
			test_exit
			ask "$current_test failed. RETRY?"
			[ $? -eq 0 ] && continue
			ask "Terminate testsuite?"
			[ $? -eq 0 ] && abort
			break
		fi
		test_exit
		break
	done

	current_device=
	current_test=
}

if [ $nr_scriptpaths -eq 0 ]; then
	# Run all scripts
	for device in $(ls "$basedir"); do
		[ -d "$basedir/$device" ] || continue
		[ "$device" == "generic" ] || request_TOP "$device" || continue

		for testscript in $(ls "$basedir/$device"); do
			do_run_test "$device" "$testscript"
		done
	done
else
	# Only run the specified tests
	let end=nr_scriptpaths-1
	for i in $(seq 0 $end); do
		scriptpath="${scriptpaths[i]}"
		device="$(echo "$scriptpath" | cut -d'/' -f1)"
		testscript="$(echo "$scriptpath" | cut -d'/' -f2)"
		[ -d "$basedir/$device" -a -f "$basedir/$device/$testscript" ] || \
			die "$scriptpath is an invalid scriptpath"
		do_run_test "$device" "$testscript"
	done
fi
cleanup
