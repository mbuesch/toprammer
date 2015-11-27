#!/bin/sh

srcdir="$(dirname "$0")"
[ "$(echo "$srcdir" | cut -c1)" = '/' ] || srcdir="$PWD/$srcdir"

srcdir="$srcdir" # git repos root

die() { echo "$*"; exit 1; }

# Import the makerelease.lib
# http://bues.ch/gitweb?p=misc.git;a=blob_plain;f=makerelease.lib;hb=HEAD
for path in $(echo "$PATH" | tr ':' ' '); do
	[ -f "$MAKERELEASE_LIB" ] && break
	MAKERELEASE_LIB="$path/makerelease.lib"
done
[ -f "$MAKERELEASE_LIB" ] && . "$MAKERELEASE_LIB" || die "makerelease.lib not found."

hook_get_version()
{
	local file="$1/libtoprammer/main.py"
	local major="$(cat "$file" | grep -e VERSION_MAJOR | head -n1 | cut -d'=' -f2)"
	local minor="$(cat "$file" | grep -e VERSION_MINOR | head -n1 | cut -d'=' -f2)"
	[ -n "$major" -a -n "$minor" ] ||\
		die "Failed to get version"
	version="$(printf '%d.%d' "$major" "$minor")"
}

project=toprammer
default_archives=py-sdist-bz2
makerelease "$@"
