#!/bin/bash

basedir="$PWD/$(dirname $0)"
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
