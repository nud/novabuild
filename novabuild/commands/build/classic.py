# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code


def get_dependencies(chroot, BUILD_DIR):
    control = PackageControlParser()
    control.read(os.path.join(BUILD_DIR, 'debian/control'))
    dependencies = control.source.get('Build-Depends', '')
    return [i.strip().split(None, 1)[0] for i in dependencies.split(',')]


def build_module(module, chroot, BUILD_DIR):
    DEBIAN_DIR = os.path.join('autobuild', 'debian', 'debian-%s' % module.name)

    code = system('cp -r %s %s/debian' % (DEBIAN_DIR, BUILD_DIR))
    check_code(code, module)

    print blue('Installing dependencies')
    code = chroot.system('apt-get install %s' % ' '.join(get_dependencies(chroot, BUILD_DIR)), root=True)
    check_code(code, module)

    # Write a new changelog entry...
    version = "%s-novacom.%s" % (module['Version'], module['Build-Number'])
    changelog_file = "%s/debian/changelog" % BUILD_DIR

    if not changelog_is_up_to_date(changelog_file, version):
        print blue("Update ChangeLog")
        old_file = "%s/changelog" % DEBIAN_DIR
        prepend_changelog_entry(changelog_file, old_file, module.name, version, "* New build.")

        # backup the new changelog file
        code = system('cp -f %s %s' % (changelog_file, old_file))
        check_code(code, module)

    # Build the package for real.
    print blue("Building '%s' '%s'" % (module.name, module['Version']))
    code = chroot.system('dpkg-buildpackage', root=True, cwd='/home/%s/tmp-build-dir/%s-%s'
                         % (chroot.user, module.name, module['Version']))
    check_code(code, module)

