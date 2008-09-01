# -*- coding: utf-8 -*- ex:set ts=4 et:

import re
import os
import sys
import tempfile
import time
from email.Utils import formatdate
from exceptions import Exception


DEFAULT_AUTHOR = "Damien Sandras"
DEFAULT_EMAIL = "dsandras@novacom.be"


# Simple class for comparing debian versions.
class Version(object):
    PATTERN = re.compile('^(?:([0-9]+):)?([0-9\.]+)(?:-novacom.([0-9]+))?$')

    def __init__(self, string):
        matches = self.PATTERN.match(string)
        if not matches:
            raise Exception("Invalid version number: %s" % string)
        self.packaging = int(matches.group(1) or 0)
        self.numbers = [int(i) for i in matches.group(2).split('.')]
        self.buildnumber = int(matches.group(3) or 0)

    def __cmp__(self, other):
        return cmp(self.packaging, other.packaging) or \
               cmp(self.numbers, other.numbers) or \
               cmp(self.buildnumber, other.buildnumber)

    def __str__(self):
        s = '.'.join(str(i) for i in self.numbers)
        if self.packaging:
            s = "%d:%s" % (self.packaging, s)
        if self.buildnumber:
            s = "%s-novacom.%d" % (s, self.buildnumber)
        return s


# Example of changelog line:
#   asterisk (1:1.2.24-novacom.1) stable; urgency=low
# Pattern used in parsechangelog/debian:
#   m/^(\w[-+0-9a-z.]*) \(([^\(\) \t]+)\)((\s+[-+0-9a-z.]+)+)\;/i
def parse_changelog_header(line):
    matches = re.match('^(\w[-+0-9a-z.]*) \(([^\(\) \t]+)\)', line, re.I)
    return matches.group(1), Version(matches.group(2))


# Do we need to update the changelog?
def changelog_is_up_to_date(filename, version):
    if not isinstance(version, Version):
        version = Version(version)
    line = file(filename, 'r').readline()
    lp, lv = parse_changelog_header(line)

    # We don't want to allow diminishing the current version number.
    if version < lv:
        raise Exception('The new version number is lower than the old one!')

    # The changelog is up to date iff the old version is the same as the new one.
    return version == lv


def read_last_changelog_entry(filename):
    f = file(filename, 'r')
    lines = [f.readline()]
    line = f.readline()
    while line.isspace() or line.startswith(' '):
        lines.append(line)
        line = f.readline()

    return lines


# Let an user edit a string
def run_editor(text):
    # Write a temporary file
    fd, filename = tempfile.mkstemp(prefix="test-vim-", suffix=".txt")
    os.fdopen(fd, "w").write(text)

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


CHANGELOG_TEMPLATE = """#
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
def prepend_changelog_entry(new_filename, old_filename, package, version):
    last_entry = ''.join('# %s' % l for l in read_last_changelog_entry(old_filename))

    text = CHANGELOG_TEMPLATE % { 'package': package,
                                  'version': version,
                                  'author': os.getenv('NOVABUILD_AUTHOR', DEFAULT_AUTHOR),
                                  'email': os.getenv('NOVABUILD_EMAIL', DEFAULT_EMAIL),
                                  'date': formatdate(localtime=True),
                                  'last_entry': last_entry }
    text = run_editor(text)

    # We don't want to continue if there is no changelog!
    if not text:
        raise Exception("No changelog provided.")

    fp = file(new_filename, 'w')
    fp.write("%s (%s) stable; urgency=low\n\n" % (package, version))
    fp.write(text)
    fp.write('\n')

    # ... and put the old content in.
    fp2 = file(old_filename, 'r')
    for line in fp2:
        fp.write(line)
