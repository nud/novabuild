# -*- coding: utf-8 -*- ex:set ts=4 et:

import re
from email.Utils import formatdate
from exceptions import Exception


# Simple class for comparing debian versions.
class Version(object):
    PATTERN = re.compile('^(?:([1-9]+):)?([1-9\.]+)(?:-novacom.([0-9]+))?$')

    def __init__(self, string):
        matches = self.PATTERN.match(string)
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


# Update the changelog with a new entry.
def prepend_changelog_entry(new_filename, old_filename, package, version, message):
    fp = file(new_filename, 'w')
    fp.write("%s (%s) stable; urgency=low\n\n" % (package, version))
    print message.split('\n')
    for line in message.split('\n'):
        fp.write("  %s\n" % line);
    fp.write(" -- Damien Sandras <dsandras@novacom.be>  %s\n\n" % formatdate(localtime=True))

    # ... and put the old content in.
    fp2 = file(old_filename, 'r')
    for line in fp2:
        fp.write(line)
