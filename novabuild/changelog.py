# -*- coding: utf-8 -*- ex:set ts=4 et:

import re
import os
import shutil
import subprocess
import sys
import tempfile
import time
from email.Utils import formatdate
from exceptions import Exception


DEFAULT_AUTHOR = "Novabuild"
DEFAULT_EMAIL = "support@beip.be"


# Example of changelog line:
#   asterisk (1:1.2.24-12+b1) stable; urgency=low
# Pattern used in parsechangelog/debian:
#   m/^(\w[-+0-9a-z.]*) \(([^\(\) \t]+)\)((\s+[-+0-9a-z.]+)+)\;/i
def parse_changelog_header(line):
    matches = re.match('^(\w[-+0-9a-z.]*) \(([^\(\) \t]+)\) (.*)$', line, re.I)
    return matches.group(1), matches.group(2), matches.group(3)


def compare_versions(v1, op, v2):
    return subprocess.call(['dpkg', '--compare-versions', v1, op, v2]) == 0


# Do we need to update the changelog?
def changelog_is_up_to_date(filename, version):
    line = file(filename, 'r').readline()
    lp, lv, ls = parse_changelog_header(line)

    # The changelog is up to date iff the old version is the same as the new one.
    if compare_versions(version, 'eq', lv):
        return True

    # We don't want to allow diminishing the current version number.
    if compare_versions(version, 'lt', lv):
        raise Exception('The new version number (%s) is lower than the old one (%s)!' % (version, lv))

    return False


def read_last_changelog_entry(filename):
    f = file(filename, 'r')
    lines = [f.readline().decode('utf-8')]
    line = f.readline().decode('utf-8')
    while line.isspace() or line.startswith(' '):
        lines.append(line)
        line = f.readline().decode('utf-8')

    return lines


# Let an user edit a string
def run_editor(text):
    # Write a temporary file
    fd, filename = tempfile.mkstemp(prefix="test-vim-", suffix=".txt")
    os.fdopen(fd, "w").write(text.encode('utf-8'))

    # Edit the file using the editor
    os.system("%s \"%s\"" % (os.getenv('EDITOR', 'vi'), filename))

    # Read the file (stripping comments) and delete it
    lines = [l for l in file(filename).readlines() if not l.startswith('#')]
    os.unlink(filename)

    # Drop double empty lines and empty lines at the begining and the end.
    lines = [lines[i] for i in range(0, len(lines))
               if i > 0 and not lines[i-1].isspace() or not lines[i].isspace()]
    if len(lines) > 1 and lines[-1].isspace():
        del lines[-1]

    return ''.join(lines)


CHANGELOG_TEMPLATE = u"""#
# Changelog entry for:
#
#         %(package)s - %(version)s
#
# Edit the lines below to reflect what has changed since the last release.
# Commented lines will not be included.
# If this file is left empty, then the building process will abord.
# Please note that wrong whitespacing might make the build process fail.
#

  * New build

 -- %(author)s <%(email)s>  %(date)s

#
# Here is the Changelog entry for the previous release:
#
%(last_entry)s
"""


# Update the changelog with a new entry.
def prepend_changelog_entry(filename, package, version):
    last_entry = ''.join('# %s' % l for l in read_last_changelog_entry(filename))

    text = CHANGELOG_TEMPLATE % { 'package': package,
                                  'version': version,
                                  'author': os.getenv('NOVABUILD_AUTHOR', DEFAULT_AUTHOR).decode('utf-8'),
                                  'email': os.getenv('NOVABUILD_EMAIL', DEFAULT_EMAIL).decode('utf-8'),
                                  'date': formatdate(localtime=True),
                                  'last_entry': last_entry }
    text = run_editor(text)

    # We don't want to continue if there is no changelog!
    if not text:
        raise Exception("No changelog provided.")

    tmp_filename = filename + '.new'
    fp = open(tmp_filename, 'w')
    fp.write("%s (%s) stable; urgency=low\n\n" % (package, version))
    fp.write(text)
    fp.write('\n')

    # ... and put the old content in.
    fp2 = open(filename, 'r')
    for line in fp2:
        fp.write(line)

    fp2.close()
    fp.close()

    os.rename(tmp_filename, filename)

# Copy the changelog, but alter the version number of the last entry to append
# the build tag
def copy_changelog_with_build_tag(srcfile, dstfile, build_tag):
    # If there is no build tag, things are easy.
    if not build_tag:
        shutil.copy2(srcfile, dstfile)
        return

    # Otherwise...
    sfp = open(srcfile, 'r')
    fp = open(dstfile, 'w')

    lp, lv, ls = parse_changelog_header(sfp.readline())
    fp.write('%s (%s) %s' % (lp, lv + build_tag, ls))

    for line in sfp:
        fp.write(line)

    sfp.close()
    fp.close()
