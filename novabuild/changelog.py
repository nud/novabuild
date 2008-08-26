# -*- coding: utf-8 -*- ex:set ts=4 et:

from email.Utils import formatdate

# Do we need to update the changelog?
def changelog_is_up_to_date(filename, version):
    line = file(filename, 'r').readline()
    return version in line

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
