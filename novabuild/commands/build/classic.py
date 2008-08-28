# -*- coding: utf-8 -*- ex:set ts=4 et:

import os

import base
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code


class BuildMethod(base.BuildMethod):
    # Set up the dpkg environment for the build.
    def setup_build_env(self, debian_dir, build_dir, module):
        code = system('cp -r %s %s/debian' % (debian_dir, build_dir))
        check_code(code, module)


    # Get the dependencies of the current package
    def get_dependencies(self, build_dir):
        control = PackageControlParser()
        control.read(os.path.join(build_dir, 'debian/control'))
        dependencies = control.source.get('Build-Depends', '')
        return [i.strip().split(None, 1)[0] for i in dependencies.split(',')]


    # Install the current module dependencies
    def install_dependencies(self, module, build_dir):
        deps = self.get_dependencies(build_dir)
        code = self.chroot.system('apt-get install %s' % ' '.join(deps), root=True)
        check_code(code, module)


    # Write a new changelog entry...
    def update_changelog(self, module, build_dir, debian_dir):
        filename = os.path.join(build_dir, 'debian', 'changelog')
        version = "%s-novacom.%s" % (module['Version'], module['Build-Number'])
        if 'Packaging-Version' in module:
            version = '%s:%s' % (module['Packaging-Version'], version)

        if not changelog_is_up_to_date(filename, version):
            old_filename = os.path.join(debian_dir, 'changelog')

            print blue("Update ChangeLog for version %s" % version)
            prepend_changelog_entry(filename, old_filename, module.name, version)

            # backup the new changelog file
            code = system('cp -f %s %s' % (filename, old_filename))
            check_code(code, module)
        else:
            print blue("No ChangeLog update is needed")


    # Build the module
    def build(self, module):
        cwd = self.chroot.abspath('~/tmp-build-dir/%s-%s' % (module.name, module['Version']))
        code = self.chroot.system('fakeroot dpkg-buildpackage', cwd=cwd)
        check_code(code, module)


    def build_module(self, module, build_dir):
        debian_dir = os.path.join('autobuild', 'debian', 'debian-%s' % module.name)

        print blue('Set up dpkg build environment')
        self.setup_build_env(debian_dir, build_dir, module)

        print blue('Installing dependencies')
        self.install_dependencies(module, build_dir)

        self.update_changelog(module, build_dir, debian_dir)

        print blue("Building '%s' '%s'" % (module.name, module['Version']))
        self.build(module)
