#!/usr/bin/env python3

import subprocess
import os
import os.path
import sys
import fcntl
import getopt
import datetime

# Eints authentification
eints_login_file = "user.cfg"

# Commit credentials
commit_user = "translators <translators@openttd.org>"
commit_message = "Update: Translations from eints\n"

# Source structure
git_remote = "origin"
git_branch = "master"
git_remote_branch = git_remote + "/" + git_branch

# External tools
lang_sync_command = "./lang_sync"
git_command = "git"

# Temporary files
lock_file = "/tmp/eints.lock"
msg_file = "/tmp/eints.msg"


class Settings:
    def __init__(self):
        self.base_url = None
        self.project = None
        self.lang_dir = None
        self.unstable_lang_dir = None
        self.lang_file_ext = None
        self.working_copy = None

    def get_lang_sync_params(self):
        result = [
            "--user-password-file",
            eints_login_file,
            "--base-url",
            self.base_url,
            "--project",
            self.project,
            "--lang-dir",
            self.lang_dir,
            "--lang-file-ext",
            self.lang_file_ext,
        ]
        if self.unstable_lang_dir:
            result.extend(["--unstable-lang-dir", self.unstable_lang_dir])
        return result

    def get_working_dirs(self):
        result = [self.lang_dir]
        if self.unstable_lang_dir:
            result.append(self.unstable_lang_dir)
        return result


class FileLock:
    """
    Inter-process lock mechanism via exclusive file locking.
    """

    def __init__(self, name):
        self.name = name
        self.file = None

    def __enter__(self):
        assert self.file is None

        self.file = open(self.name, "a")
        try:
            fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except Exception:
            self.file.close()
            self.file = None
            raise
        self.file.truncate()
        self.file.write("pid:{} date:{:%Y-%m-%d %H:%M:%S}\n".format(os.getpid(), datetime.datetime.now()))
        self.file.flush()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.file is not None

        os.remove(self.name)
        fcntl.flock(self.file, fcntl.LOCK_UN)
        self.file.close()

        self.file = None

        return False


def print_info(msg):
    """
    Print info message.

    @param msg: Message
    @type  msg: C{str}
    """

    print("[{:%Y-%m-%d %H:%M:%S}] {}".format(datetime.datetime.now(), msg))


def git_status(settings):
    """
    Check whether working copy is in a valid status,
    and whether there are modifies.

    A valid state means:
     - No untracked files.
     - No added files.
     - No removed files.
    All these alterations are not allowed to be performed by eintsgit.

    @return: Whether files are modified.
    @rtype:  C{bool}
    """

    msg = subprocess.check_output(
        [git_command, "status", "-s", *settings.get_working_dirs()],
        universal_newlines=True,
    )
    return msg.strip() != ""


def git_pull(settings):
    """
    Update working copy, and revert all modifications.

    @return: Whether files were updated.
    @rtype:  C{bool}
    """

    subprocess.check_call([git_command, "fetch", git_remote])
    subprocess.check_call([git_command, "clean", "-f", os.environ.get("GIT_WORK_TREE")])
    changes = subprocess.check_output(
        [git_command, "diff", "--name-only", "HEAD.." + git_remote_branch],
        universal_newlines=True,
    )
    subprocess.check_call([git_command, "reset", "--hard", git_remote_branch])

    for line in changes.splitlines():
        if line.startswith(settings.lang_dir) >= 0:
            return True
        if settings.lang_dir and line.startswith(settings.lang_dir) >= 0:
            return True

    return False


def git_push(settings, msg_file, dry_run):
    """
    Commit and push working copy.

    @param msg_file: Path to file with commit message.
    @type  msg_file: C{str}

    @param dry_run: Do not push
    @type  dry_run: C{bool}
    """

    subprocess.check_call([git_command, "add", *settings.get_working_dirs()])
    subprocess.check_call([git_command, "commit", "--author", commit_user, "-F", msg_file])
    if not dry_run:
        subprocess.check_call([git_command, "push"])


def eints_upload(settings):
    """
    Update base language and translations to Eints.
    """

    subprocess.check_call(
        [
            lang_sync_command,
            *settings.get_lang_sync_params(),
            "upload-base",
            "upload-translations",
        ]
    )


def eints_download(settings, credits_file):
    """
    Download translations from Eints.

    @param credits_file: File for translator credits.
    @type  credits_file: C{str}
    """

    subprocess.check_call(
        [
            lang_sync_command,
            *settings.get_lang_sync_params(),
            "--credits",
            credits_file,
            "download-translations",
        ]
    )


def update_eints_from_git(settings, force):
    """
    Perform the complete operation from syncing Eints from the repository.

    @param force: Upload even if no changes.
    @type  force: C{bool}
    """

    with FileLock(lock_file):
        print_info("Check updates from git")
        if git_pull(settings) or force:
            print_info("Upload translations")
            eints_upload(settings)
        print_info("Done")


def commit_eints_to_git(settings, dry_run):
    """
    Perform the complete operation from commit Eints changes to the repository.

    @param dry_run: Do not commit, leave as modified.
    @type  dry_run: C{bool}
    """

    with FileLock(lock_file):
        # Upload first in any case.
        print_info("Update from git")
        git_pull(settings)
        print_info("Upload/Merge translations")
        eints_upload(settings)

        print_info("Download translations")
        eints_download(settings, msg_file)
        if git_status(settings):
            print_info("Commit changes")
            # Assemble commit messge
            with open(msg_file, "r+", encoding="utf-8") as f:
                cred = f.read()
                f.seek(0)
                f.truncate(0)
                f.write(commit_message)
                f.write(cred)

            git_push(settings, msg_file, dry_run)
        print_info("Done")


def run():
    """
    Run the program (it was started from the command line).
    """

    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "h",
            [
                "help",
                "force",
                "dry-run",
                "base-url=",
                "project=",
                "lang-dir=",
                "unstable-lang-dir=",
                "lang-file-ext=",
                "working-copy=",
            ],
        )
    except getopt.GetoptError as err:
        print("eintsgit: " + str(err) + ' (try "eintsgit --help")')
        sys.exit(2)

    # Parse options
    force = False
    dry_run = False
    settings = Settings()

    for opt, val in opts:
        if opt in ("--help", "-h"):
            print(
                """\
eintsgit -- Synchronize language files between git and Eints.

eintsgit <options> <operations>

with <options>:

--help
-h
    Get this help text.

--force
    See individual operations below

--dry-run
    See individual operations below

--project
    Eints project identifier

--working-copy
    Path to git working copy

--lang-dir=LANG_DIR
    Path of the directory containing the language files at the local disc.

--unstable-lang-dir=UNSTABLE_LANG_DIR
    Path of the directory containing the unstable language files at the local disc.

--lang-file-ext=LANG_EXT
    Filename suffix used by the language files.

--base-url
    URL where eints is at



and <operations>:

update-from-git
    Update working copy and upload modifications.
    With --force upload even if git reported no modifications.

commit-to-git
    Update working copy, merge and download translations from Eints, commit and push.
    With --dry-run stop before pushing and leave commits local.

"""
            )
            sys.exit(0)

        if opt == "--force":
            force = True
            continue

        if opt == "--dry-run":
            dry_run = True
            continue

        key = opt[2:].replace("-", "_")
        if hasattr(settings, key):
            if getattr(settings, key):
                print("Duplicate {} option".format(opt))
                sys.exit(2)
            setattr(settings, key, val)
            continue

        raise ValueError("Unknown option {} encountered.".format(opt))

    # Parse operations
    do_update = False
    do_commit = False

    for arg in args:
        if arg == "update-from-git":
            do_update = True
            continue

        if arg == "commit-to-git":
            do_commit = True

            continue

        print("Unknown operation: {}".format(arg))
        sys.exit(2)

    # Check options
    if do_update or do_commit:
        lsp = settings.get_lang_sync_params()
        for k, v in zip(lsp[0::2], lsp[1::2]):
            if v is None:
                print("No {} specified".format(k))
                sys.exit(2)

        if settings.working_copy:
            settings.working_copy = os.path.abspath(settings.working_copy)
            settings.lang_dir = os.path.join(settings.working_copy, settings.lang_dir)
            if settings.unstable_lang_dir:
                settings.unstable_lang_dir = os.path.join(settings.working_copy, settings.unstable_lang_dir)
            os.environ["GIT_WORK_TREE"] = settings.working_copy
            os.environ["GIT_DIR"] = os.path.join(settings.working_copy, ".git")
        else:
            print("No --working-copy specified")
            sys.exit(2)

    # Execute operations
    if do_update:
        update_eints_from_git(settings, force)

    if do_commit:
        commit_eints_to_git(settings, dry_run)

    sys.exit(0)


if __name__ == "__main__":
    run()
