#!/bin/sh
# Create source template
# Copyright (c) 2010-2012 Michael Buesch <m@bues.ch>
# Licensed under the GNU/GPL v2+

basedir="$(dirname "$0")"
[ "$(echo -n "$basedir" | cut -c1)" = "/" ] || basedir="$PWD/$basedir"

template="$basedir/template"

set -e

usage()
{
	echo "Usage: create.sh TARGET_NAME"
}

[ $# -eq 1 ] || {
	usage
	exit 1
}
name="$1"

target="$basedir/$name"

mkdir -p "$target"
for file in $(ls "$template"); do
	suffix="$(echo "$file" | cut -d. -f2)"
	targetfile="$name.$suffix"
	[ "$file" = "Makefile" ] && targetfile="$file"
	cat "$template/$file" |\
		sed -e 's/template/'"$name"'/' > "$target/$targetfile"
done

exit 0
