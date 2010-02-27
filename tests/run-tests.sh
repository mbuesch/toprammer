#!/bin/bash
# Toprammer regression tests
# Copyright (c) 2010 Michael Buesch <mb@bu3sch.de>

basedir="$PWD/$(dirname $0)"
tmpdir="/tmp/toprammer-test-$$"


function cleanup
{
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
	$basedir/../toprammer $args >$logfile 2>&1
	if [ $? -ne 0 ]; then
		[ -r "$logfile" ] && cat "$logfile"
		die "toprammer $args  <<<FAILED>>>"
	fi
}

function toprammer_layout_silent
{
	local args="$@"
	local logfile="$tmpdir/toprammer-layout.log"
	echo "        toprammer-layout $args"
	$basedir/../toprammer-layout $args >$logfile 2>&1
	if [ $? -ne 0 ]; then
		[ -r "$logfile" ] && cat "$logfile"
		die "toprammer-layout $args  <<<FAILED>>>"
	fi
}

function toprammer_layout
{
	local args="$@"
	$basedir/../toprammer-layout $args
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
	[ "$res" = "x" ] && return 1
	return 0
}

function request_DUT # $1=DUT-name
{
	local dut="$1"
	toprammer_layout -d "$current_device" -p "$dut" --only-insert
	request "Please insert a $dut into the ZIF socket (x to skip)..."
}

function request_TOP # $1=TOPxxxx
{
	request "Please connect the $@ programmer (x to skip)..."
}

function create_random_file # $1=file $2=bs $3=count
{
	dd if=/dev/urandom of=$1 bs=$2 count=$3 >/dev/null 2>&1
	[ $? -eq 0 ] || die "Failed to create $1"
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

current_test=
current_device=
cleanup
mkdir -p "$tmpdir"
[ $? -eq 0 ] || die "Failed to create $tmpdir"

# Create various test files
tmpfile="$tmpdir/tmpfile"

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
create_random_file "$testfile_4k" 1024 4

testfile_8k="$tmpdir/testfile_8k"
create_random_file "$testfile_8k" 1024 8

testfile_16k="$tmpdir/testfile_16k"
create_random_file "$testfile_16k" 1024 16

testfile_32k="$tmpdir/testfile_32k"
create_random_file "$testfile_32k" 1024 32


for device in $(ls "$basedir"); do
	devdir="$basedir/$device"
	[ -d "$devdir" ] || continue
	[ "$device" == "generic" ] || request_TOP "$device" || continue
	current_device="$device"

	for testscript in $(ls "$devdir"); do
		current_test="$device/$testscript"
		echo "Running $current_test..."
		. "$basedir/defaults.test"
		. "$devdir/$testscript"
		rm -f "$tmpfile"
		test_init
		[ $? -eq 0 ] || continue
		test_run
		test_exit
	done
done
cleanup
