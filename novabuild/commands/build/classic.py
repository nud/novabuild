# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code


# Get the dependencies of the current package
def get_dependencies(chroot, build_dir):
    control = PackageControlParser()
    control.read(os.path.join(build_dir, 'debian/control'))
    dependencies = control.source.get('Build-Depends', '')
    return [i.strip().split(None, 1)[0] for i in dependencies.split(',')]


# Install the current module dependencies
def install_dependencies(module, chroot, build_dir):
    print blue('Installing dependencies')
    code = chroot.system('apt-get install %s' % ' '.join(get_dependencies(chroot, build_dir)), root=True)
    check_code(code, module)


# Write a new changelog entry...
def update_changelog(module, build_dir, debian_dir):
    filename = os.path.join(build_dir, 'debian', 'changelog')
    version = "%s-novacom.%s" % (module['Version'], module['Build-Number'])

    if not changelog_is_up_to_date(filename, version):
        old_filename = os.path.join(debian_dir, 'changelog')

        print blue("Update ChangeLog for version %s" % version)
        prepend_changelog_entry(filename, old_filename, module.name, version, "* New build.")

        # backup the new changelog file
        code = system('cp -f %s %s' % (filename, old_filename))
        check_code(code, module)
    else:
        print blue("No ChangeLog update is needed")


def build_module(module, chroot, BUILD_DIR):
    DEBIAN_DIR = os.path.join('autobuild', 'debian', 'debian-%s' % module.name)

    code = system('cp -r %s %s/debian' % (DEBIAN_DIR, BUILD_DIR))
    check_code(code, module)

    install_dependencies(module, chroot, BUILD_DIR)

    update_changelog(module, BUILD_DIR, DEBIAN_DIR)

    # Build the package for real.
    print blue("Building '%s' '%s'" % (module.name, module['Version']))
    code = chroot.system('dpkg-buildpackage', root=True, cwd='/home/%s/tmp-build-dir/%s-%s'
                         % (chroot.user, module.name, module['Version']))
    check_code(code, module)

