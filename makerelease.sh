#!/bin/bash
set -e

project="toprammer"


origin="$PWD/$(dirname $0)"

do_git_tag=1
[ "$1" = "--notag" ] && do_git_tag=0

version_major="$(cat $origin/libtoprammer/toprammer_main.py | grep -e VERSION_MAJOR | head -n1 | cut -d'=' -f2)"
version_minor="$(cat $origin/libtoprammer/toprammer_main.py | grep -e VERSION_MINOR | head -n1 | cut -d'=' -f2)"
version="$(printf %d.%d $version_major $version_minor)"
if [ -z "$version" ]; then
	echo "Could not determine version!"
	exit 1
fi
tmpdir="/tmp"
release_name="$project-$version"
tarball="$release_name.tar.bz2"
tagname="release-$version"
tagmsg="$project-$version release"

export GIT_DIR="$origin/.git"

cd "$tmpdir"
rm -Rf "$release_name"
echo "Creating target directory..."
mkdir "$release_name"
cd "$release_name"
echo "git checkout"
git checkout -f
rm makerelease.sh

echo "Creating tarball..."
cd "$tmpdir"
tar cjf "$tarball" "$release_name"
mv "$tarball" "$origin"

echo "Running testbuild..."
cd "$tmpdir/$release_name"
./setup.py build

echo "Cleaning up..."
cd "$tmpdir"
rm -Rf "$release_name"

if [ "$do_git_tag" -ne 0 ]; then
	echo "Tagging GIT"
	cd "$origin"
	git tag -m "$tagmsg" -a "$tagname"
fi

echo
echo "Built release $tarball"
