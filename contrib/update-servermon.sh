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

set -e

# Set/edit these here if you want them hard-coded, otherwise override by optflags
merge=1
migrate=1
host_name=
repo_dir="$(readlink -e .)"
dryrun=0
updatedeps=1
archive_extension="tar"
updatedepstype="pip"
# Set these to match your web-server's configs
# e.g. parent_path=/srv && base_prefix=servermon -> /srv/servermon-XXX (XXX = commit hash)
parent_path="/srv"
base_prefix="servermon"
# Start/stop server commands to run. Offline-time is minised to the duration of
# creating a single symlink, but an even better way would be to use source-reloading,
# with the process running in WSGI daemon mode. See:
# https://code.google.com/p/modwsgi/wiki/ReloadingSourceCode
stop_server="invoke-rc.d apache2 stop"
start_server="invoke-rc.d apache2 start"
# Whether to just touch the WSGI file to auto-reload instead of restarting server
reload_wsgi=0
wsgi_file_path=

usage() {
	cat <<EOH
Usage: $script_name OPTIONS [--] [commit_hash]

OPTIONS:
 --help, -h                 : this message
 --dry-run, -d              : do a dry-run, echoing invasive commands instead
                              of executing them
 --no-update-deps, -D       : don't attempt to install/update dependency
                              packages
 --no-merge, -m             : don't compare your config changes in an editor
 --no-migrate, -M           : don't run South migrations command
 --update-deps-type, -u "X" : which type of update to use for deps
                              (options: pip,apt,aptitude - default: pip)
 --host, -H "X"             : override the server hostname
 --repo-dir, -r "X"         : where is the repo? (default: current directory)
 --reload-wsgi-daemon, -R   : if running in WSGI daemon mode and can reload by
                              touching the WSGI file, rather than restart
 --archive-extension, -e "X": extension used by git-archive (default: tar)
 --parent-path, -p "X"      : set this to the parent directory for the files
                              (default: /srv)
 --base-prefix, -b "X"      : prefix of dir-name for files (default: servermon)
 --stop-server, -s "X"      : command for stopping the server in restart-mode
                              (default: invoke-rc.d apache2 stop)
 --start-server, -S "X"     : command for starting the server in restart-mode
                              (default: invoke-rc.d apache2 start)
 --wsgi-file-path, -w "X"   : path of WSGI file in reload-mode
                              (default: the pre-supplied apache wsgi file)

NOTES:

 This should work fine (without requiring custom steps) for updating servermon
 from version 0.4 and later (if there are no installer-bugs, of course...) from
 a checked out servermon git repo.

 It works by presuming the following things (replace the COMMIT_HASH bits of
 course, and file names will be whatever you set them to, but the concept is
 the same):
  * servermon is already installed and operational at
    \$parent_path/\$base_prefix-OLD_COMMIT_HASH
  * \$parent_path/\$base_prefix is a symlink pointing to \$base_prefix-OLD_COMMIT_HASH
  * you need to have non-interactive (key-only-based) ssh access to the server
  * you need to have the ability to do non-interactive (passwordless) "sudo -s"

 The editor which is used for comparing files on the server during the "merge"
 phase is taken from your \$EDITOR setting on the server. Override that in
 your environment accordingly if you wish to change it. Use of a
 "visual-compare" tool like "meld" as the editor is highy recommended, and of
 course be careful not to update the *existing* version of each file as this
 may affect the presently running server in unpredictable ways.

 It is highly recommended to do a "--dry-run" pass before running the command
 for real, just to be prudent. If you don't understand what it is about to run,
 don't run it...

 The --reload-wsgi-daemon option touches the wsgi file in the apache subdir.
 This should work when running as a daemon process under any server, but if you
 are running a custom wsgi file then you will need to do this step manually.

 This script deals with commit hashes rather than release version-numbers but
 the servermon docs advise not updating more than one release-version at a
 time. Until there is time to put error-checking in the code which can grok
 releases' correlation to commits, and to add code to do an
 untar/symlink/migrations tango through one release-version at a time until it
 reaches the desired commit, for now this script just plays dumb and will
 happily try to upgrade straight to whatever commit you tell it to (or the
 latest commit, if you don't specify). This means you have to know how far to
 upgrade at a time. If not you will probably end up in a swampy tangled
 migrations-nightmare which will gnaw away at your soul. This is no worse than
 the mess you would be in if you did the same thing upgrading manually though,
 so it in no way diminishes the usefulness of this script, it just adds to the
 TODO list...

 Recent versions of Django have changed file-layout. This installer defaults to
 expecting the new layout. If your upgrade involves the old layout this will
 not work (for now) without a tiny change to the script (or use dry-run and
 copy the commands manually, tweaking where needed). Keep in mind also that for
 old-Django to new-Django the .dist-based files will not be copied across (yet)
 because they won't be found in the expected places. For now you have to ignore
 the script output and do that step manually if you strike that problem (and it
 will ony happen once).
EOH
}

# getopts
script_name="`printf '%s' "$0" | sed -e 's:^.*/\([^/]\+\)$:\1:'`"
while test -n "$1"; do
	case "$1" in
	--help|-h)
		usage
		exit 0;;
	--dry-run|-d)
		dryrun=1
		shift
		continue;;
	--no-update-deps|-D)
		updatedeps=0
		shift
		continue;;
	--no-merge|-m)
		merge=0
		shift
		continue;;
	--no-migrate|-M)
		migrate=0
		shift
		continue;;
	--update-deps-type|-u)
		case "$2" in
		pip|apt|aptitude)
			updatedepstype="$2"
			shift 2
			continue;;
		*)
			usage >&2
			printf '* Invalid --update-deps-type argument: %s\n' "$2" >&2
			exit 1;;
		esac;;
	--host|-H)
		host_name="$2"
		shift 2
		continue;;
	--repo-dir|-r)
		repo_dir="$(readlink -e "$2")"
		shift 2
		continue;;
	--reload-wsgi-daemon|-R)
		reload_wsgi=1
		shift
		continue;;
	--archive-extension|-e)
		archive_extension="$2"
		shift 2
		continue;;
	--parent-path|-p)
		parent_path="$2"
		shift 2
		continue;;
	--base-prefix|-b)
		base_prefix="$2"
		shift 2
		continue;;
	--stop-server|-s)
		stop_server="$2"
		shift 2
		continue;;
	--start-server|-S)
		start_server="$2"
		shift 2
		continue;;
	--wsgi-file-path|-w)
		wsgi_file_path="$2"
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

# setup
if test -z "$host_name"; then
	printf '%s: must specify host_name.\n' "$script_name" >&2
	exit 1
fi
today=`date +%Y%m%d`
cd "$repo_dir"
# use specified commit or the "latest" one
if test $# -gt 0; then
	commit_hash="$1"
else
	printf "You didn't specify a commit to update to, so I am defaulting to the latest. Are\n" >&2
	printf "you *sure* that's what you want?\n" >&2
	if test 1 -ne $dryrun; then
		printf "Sleeping for 5 seconds so you can interrupt me if not...  ;-)\n" >&2
		sleep 5
	fi
	commit_hash=`git show --pretty=format:%H HEAD | head -n 1`
fi
# setup unarchive command
case "$archive_extension" in
	tar) unarchive_cmd='tar xpf';;
	tar.gz) unarchive_cmd='tar xpzf';;
	tar.bz2) unarchive_cmd='tar xpjf';;
	tar.xz) unarchive_cmd='tar xpJf';;
	tar.Z) unarchive_cmd='tar xpZf';;
	*) printf 'Archive format not yet recognised.\n' >&2; exit 1;;
esac
# set commands to run on server
ssh_cmds="\
set -e;
HOME=\"\${HOME:-\$(printf '%s' ~)}\";
! test '~' = \"\$HOME\" || HOME=\"/home/\`id -urn\`\";
sudo -s -n;
cd '$parent_path';
$unarchive_cmd \"\${HOME}/servermon-${today}-${commit_hash}.${archive_extension}\";
if test 1 -eq $updatedeps; then #UPDATE_DEPS
	cd '${base_prefix}-${commit_hash}';
	case $updatedepstype in
	pip)
		pip install -r requirements.txt;;
	apt|aptitude)
		deps=\`cat requirements.txt\`;
		if printf '%s' '\$deps' | grep -q ','; then
			printf '%s: Version definitions with commas not yet supported for non-pip deps-updating.\n' '$script_name' >&2;
			# TODO: I doubt apt(itude) would like e.g. 'Django>=1.2,<1.5'. Getting this working will most likely involve
			# 'sed/awk' to split the version number and operator, 'case' to step through actions based on operator, and
			# 'dpkg --compare-versions' to compare output of 'apt-cache show'.
			exit 1;
		fi;
		$updatedepstype install \$deps;;
	esac;
	cd ..;
fi;
for distfile in \`find '${base_prefix}-${commit_hash}' -name '*.dist' -printf '%P\n'\`; do
	nondistfile=\"\$(printf '%s' \"\$distfile\" | sed -e '$ s/\.dist$//')\";
	if test -e \"${base_prefix}/\${nondistfile}\"; then
		cp \"${base_prefix}/\${nondistfile}\" \"${base_prefix}-${commit_hash}/\${nondistfile}\";
	else
		cp \"${base_prefix}-${commit_hash}/\${distfile}\" \"${base_prefix}-${commit_hash}/\${nondistfile}\";
	fi;
	if test 1 -eq $merge; then #MERGE
		\${EDITOR:-vi} \"${base_prefix}-${commit_hash}/\${distfile}\" \"${base_prefix}-${commit_hash}/\${nondistfile}\";
	fi;
done;
if test 1 -eq $migrate; then #MIGRATE
	for migrations_dir in '${base_prefix}/servermon'/*/migrations; do
		migrations_destdir=\"\$(printf '%s' \"\$migrations_dir\" | sed -e 's:^${base_prefix}:${base_prefix}-${commit_hash}:')\";
		cp -a \"\$migrations_dir\" \"\$migrations_destdir\";
	done;
	cd '${base_prefix}-${commit_hash}/servermon';
	./manage.py migrate;
	cd ../..;
fi;
chown -R www-data:www-data '${base_prefix}-${commit_hash}';
chmod -R ug=rwX,o= '${base_prefix}-${commit_hash}';
wsgi_file_path='${wsgi_file_path:-${base_prefix}-${commit_hash}/servermon/apache/django.wsgi}';

if test 1 -eq $reload_wsgi; then #RELOAD_WSGI
	touch '$wsgi_file_path';
	rm -f '${base_prefix};
	ln -sf '${base_prefix}-${commit_hash}' '${base_prefix}';
else
	$stop_server;
	rm -f '${base_prefix};
	ln -sf '${base_prefix}-${commit_hash}' '${base_prefix}';
	$start_server;
fi
"

# export a commit snapshot, then send to server
if test 1 -eq $dryrun; then
	printf '%s\n' "git archive --prefix=${base_prefix}-${commit_hash}/ -o servermon-${today}-${commit_hash}.${archive_extension} $commit_hash"
	printf '%s\n' "scp servermon-${today}-${commit_hash}.${archive_extension} \"${host_name}:\""
	printf '%s\n' "rm -f servermon-${today}-${commit_hash}.${archive_extension}"
else
	git archive --prefix=${base_prefix}-${commit_hash}/ -o servermon-${today}-${commit_hash}.${archive_extension} $commit_hash
	scp servermon-${today}-${commit_hash}.${archive_extension} "${host_name}:"
	rm -f servermon-${today}-${commit_hash}.${archive_extension}
fi
# login to server and run commands
if test 1 -eq $dryrun; then #DRYRUN
	printf '%s\n' "ssh \"$host_name\" \"\"\"
$(printf '%s\n' "$ssh_cmds" | sed -e 's/^/> /')
\"\"\""
else
	ssh "$host_name" "$ssh_cmds"
fi
