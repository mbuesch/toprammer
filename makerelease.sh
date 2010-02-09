#!/bin/bash
set -e

project="toprammer"


origin="$(pwd)"
version_major="$(cat $origin/toprammer | grep -e VERSION_MAJOR | head -n1 | cut -d'=' -f2)"
version_minor="$(cat $origin/toprammer | grep -e VERSION_MINOR | head -n1 | cut -d'=' -f2)"
version="$(printf %d.%d $version_major $version_minor)"
if [ -z "$version" ]; then
	echo "Could not determine version!"
	exit 1
fi
release_name="$project-$version"
tarball="$release_name.tar.bz2"
tagname="release-$version"
tagmsg="$project-$version release"

export GIT_DIR="$origin/.git"

cd /tmp/
rm -Rf "$release_name"
echo "Creating target directory"
mkdir "$release_name"
cd "$release_name"
echo "git checkout"
git checkout -f

rm makerelease.sh

echo "creating tarball"
cd ..
tar cjf "$tarball" "$release_name"
mv "$tarball" "$origin"
rm -Rf "$release_name"

echo "Tagging GIT"
cd "$origin"
git tag -m "$tagmsg" -a "$tagname"

echo
echo "built release $version"
