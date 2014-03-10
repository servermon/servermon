#!/bin/sh

## update-servermon.sh:
#    version 0.1 - the "prototype-I-haven't-actually-run-yet" version

##
# By Rowan Thorpe.
#
#  Licensed in what ever way fits with the servermon licensing *if* this is
#  added to its contrib directory [if so, servermon maintainers please update
#  this text accordingly]. If this *isn't* added though, then it can live out
#  its days in the Wilderness of Forgotten Github Gists (cue spooky music),
#  under:
#
#    "The Sledgehammer Reader License Agreement"
#
#  which I happily discovered at:
#
#    http://club.myce.com/f1/most-stupid-license-agreement-66027/#post401056
#
#  and which makes for a nice waste of 5 minutes you'll never get back...
##

# ...but seriously though...

##
# This should work fine (without requiring custom steps) for updating servermon
# from version 0.4 and later (if there are no bugs, of course...) from a
# checked out servermon git repo.
#
# It works by presuming the following things (replace the COMMIT_HASH bits of
# course, and file names will be whatever you set them too, but the concept is
# the same):
#
#  * servermon is already installed and operational at
#    /srv/servermon-OLD_COMMIT_HASH
#
#  * /srv/servermon is a symlink pointing to /srv/servermon-OLD_COMMIT_HASH
#
#  * you need to have non-interactive (key-only-based) ssh access to the server
#
#  * you need to have the ability to do non-interactive (passwordless)
#    "sudo -s"
##

#  NB: This script deals with commit hashes rather than release version-numbers
#      but the servermon docs advise not updating more than one release-version
#      at a time. Until there is time to put error-checking in the code which
#      can grok releases' correlation to commits, and to add code to do an
#      untar/symlink/migrations tango through one release-version at a time
#      until it reaches the desired commit, for now this script just plays dumb
#      and will happily try to upgrade straight to whatever commit you tell it
#      to (or the latest commit, if you don't specify). This means you have to
#      know how far to upgrade at a time. If not you will probably end up in a
#      swampy tangled migrations-nightmare which will gnaw away at your soul.
#      This is no worse than the mess you would be in if you did the same thing
#      upgrading manually though, so it in no way diminishes the usefulness of
#      this script, it just adds to the TODO list...

set -e

# Set/edit these here if you want them hard-coded, otherwise override by optflags
merge=1
migrate=1
host_name=
repo_dir="$(readlink -e .)"

# Set these to match your web-server's configs
# e.g. parent_path=/srv && base_prefix=servermon -> /srv/servermon-XXX (XXX = commit hash)
parent_path="/srv"
base_prefix="servermon"
# Start/stop server commands to run. Offline-time is minised to the duration of
# creating a single symlink, but an even better way would be to use source-reloading,
# with the process running in WSGI daemon mode. See:
# https://code.google.com/p/modwsgi/wiki/ReloadingSourceCode
stop_server="invoke-rc.d apache stop"
start_server="invoke-rc.d apache start"

usage() {
	cat <<EOH
Usage: $script_name OPTIONS [--] [commit_hash]

OPTIONS:
 --help, -h             : this message
 --no-merge, -m         : don't compare your config changes in an editor
 --no-migrate, -M       : don't run South migrations command
 --host "X", -H "X"     : override the server hostname
 --repo-dir "X", -r "X" : where is the git repo? (defaults to "current directory")
EOH
}

# getopts
script_name="`printf '%s' "$0" | sed -e 's:^.*/\([^/]\+\)$:\1:'`"
while test -n "$1"; do
	case "$1" in
	--help|-h)
		usage
		exit 0;;
	--no-merge|-m)
		merge=0
		shift
		continue;;
	--no-migrate|-M)
		migrate=0
		shift
		continue;;
	--host|-H)
		host_name="$2"
		shift 2
		continue;;
	--repo-dir|-r)
		repo_dir="$(readlink -e "$2")"
		shift 2
		continue;;
	--)
		shift
		break;;
	-*)
		usage >&2
		exit 1;;
	*)
		break;;
	esac
done

cd "$repo_dir"
# setup
if test -z "$host_name"; then
	printf '%s: must specify host_name.\n' "$script_name" >&2
	exit 1
fi
USER="${USER:-\`id -urn\`}"
today=`date +%Y%m%d`
# use specified commit or the "latest" one
if test $# -gt 0; then
	commit_hash="$1"
else
	commit_hash=`git show --pretty=format:%H HEAD`
fi
# export a commit snapshot
git archive --prefix=${base_prefix}-${commit_hash}/ -o servermon-${today}-${commit_hash}.tar.xz
# send archive to server
scp servermon-${today}-${commit_hash}.tar.xz "${host_name}:"
# set commands to run on server
ssh_cmds="\
set -e;\
sudo -s -n;\
HOME=\"\${HOME:-/home/$USER}\";\
cd \"$parent_path\";\
tar xpJf \"\${HOME}/servermon-${today}-${commit_hash}.tar.xz\";\
chown -R www-data:www-data \"${base_prefix}-${commit_hash}\";\
chmod -R ug=rwX,o= \"${base_prefix}-${commit_hash}\";\
if test -e \"${base_prefix}/urls.py\"; then\
	cp \"${base_prefix}/urls.py\" \"${base_prefix}-${commit_hash}/urls.py\";\
else\
	cp \"${base_prefix}-${commit_hash}/urls.py.dist\" \"${base_prefix}-${commit_hash}/urls.py\";\
fi;\
if test -e \"${base_prefix}/settings.py\"; then\
	cp \"${base_prefix}/settings.py\" \"${base_prefix}-${commit_hash}/settings.py\";\
else\
	cp \"${base_prefix}-${commit_hash}/settings.py.dist\" \"${base_prefix}-${commit_hash}/settings.py\";\
fi;\
if test \"$merge\" = 1; then\
	\"\$EDITOR\" \"${base_prefix}-${commit_hash}/urls.py\" \"${base_prefix}-${commit_hash}/urls.py.dist\";\
	\"\$EDITOR\" \"${base_prefix}-${commit_hash}/settings.py\" \"${base_prefix}-${commit_hash}/settings.py.dist\";\
fi;\
if test \"$migrate\" = 1; then\
	cd \"${base_prefix}-${commit_hash}\";\
	./manage.py migrate;\
	cd ..;\
fi;\
$stop_server;\
ln -sf \"${base_prefix}\" \"${base_prefix}-${commit_hash}\";\
$start_server;\
'

# login to server and run commands
ssh '$host_name' "$ssh_cmds"
