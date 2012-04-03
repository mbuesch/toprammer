#!/bin/bash
# Create source template
# Copyright (c) 2010 Michael Buesch <m@bues.ch>
# Licensed under the GNU/GPL v2+

basedir="$(dirname "$0")"
[ "${basedir:0:1}" = "/" ] || basedir="$PWD/$basedir"

template="$basedir/template"

set -e

function usage
{
	echo "Usage: create.sh TARGET_NAME"
}

if [ $# -ne 1 ]; then
	usage
	exit 1
fi
name="$1"

target="$basedir/$name"

mkdir -p "$target"
for file in $(ls $template); do
	suffix="$(echo $file | cut -d. -f2)"
	targetfile="$name.$suffix"
	[ $file != Makefile ] || targetfile=$file
	cat $template/$file | sed -e 's/template/'$name'/' >$target/$targetfile
done

exit 0
