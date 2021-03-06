# -*- coding: utf-8 -*- ex:set ts=4 et:

import jinja2
import os
import shutil

import base
from novabuild.debcontrol import PackageControlParser
from novabuild.changelog import *
from novabuild.run import system, check_code
from novabuild.colours import blue
from novabuild.fileops import copytree_j2


def _read_template(filename):
    contents = open(filename).read().decode('utf-8')
    mtime = os.path.getmtime(filename)

    def uptodate():
        try:
            return os.path.getmtime(filename) == mtime
        except OSError:
            return False

    return contents, filename, uptodate


class BuildMethod(base.BuildMethod):
    def get_debian_dir(self, module):
        return os.path.join('debian', 'debian-%s' % module.name)

    def get_jinja_env(self):
        return jinja2.Environment(loader=jinja2.FunctionLoader(_read_template))

    # Set up the dpkg environment for the build.
    def setup_build_env(self, debian_dir, build_dir, module):
        self.uncompress_tarball(module, build_dir)

        # Remove the debian dir that would be distributed with the upstream tarball.
        target_debian_dir = os.path.join(build_dir, 'debian')
        if (os.path.exists(target_debian_dir)):
            shutil.rmtree(target_debian_dir)

        copytree_j2(debian_dir, target_debian_dir, self.get_jinja_env(), self.args.vars)


    # Get the dependencies of the current package
    def get_dependencies(self, build_dir):
        control = PackageControlParser()
        control.read(os.path.join(build_dir, 'debian/control'))
        dependencies = control.source.get('Build-Depends', '')
        return [i.strip().split(None, 1)[0] for i in dependencies.split(',') if i]


    # Install the current module dependencies
    def install_dependencies(self, module, build_dir):
        deps = self.get_dependencies(build_dir)
        if deps:
            code = system('apt-get install %s' % ' '.join(deps), root=True)
            check_code(code, module)


    def get_version(self, module):
        version = "%s-%s" % (module['Version'], self.args.revision_pattern % module['Build-Number'])
        if 'Packaging-Version' in module:
            version = "%s:%s" % (module['Packaging-Version'], version)
        return version


    # Write a new changelog entry...
    def update_changelog(self, module, build_dir, debian_dir):
        filename = os.path.join(debian_dir, 'changelog')
        build_filename = os.path.join(build_dir, 'debian', 'changelog')
        version = self.get_version(module)

        if not changelog_is_up_to_date(filename, version):
            print blue("Update ChangeLog for version %s" % version)
            prepend_changelog_entry(filename, module.name, version)
        else:
            print blue("No ChangeLog update is needed")

        copy_changelog_with_build_tag(filename, build_filename, self.args.build_tag)


    # Build the module
    def build(self, module):
        cwd = os.path.expanduser('~/tmp-build-dir/%s-%s' % (module.name, module['Version']))
        code = system('pwd; dpkg-buildpackage -rfakeroot -b -uc', cwd=cwd)
        check_code(code, module)


    def build_module(self, module, build_dir):
        debian_dir = self.get_debian_dir(module)

        print blue('Set up dpkg build environment')
        self.setup_build_env(debian_dir, build_dir, module)

        print blue('Installing dependencies')
        self.install_dependencies(module, build_dir)

        self.update_changelog(module, build_dir, debian_dir)

        print blue("Building '%s' '%s'" % (module.name, module['Version']))
        self.build(module)

    def list_module_packages(self, module):
        debiandir = self.get_debian_dir(module)

        control = PackageControlParser()

        if os.path.exists(os.path.join(debiandir, 'control')):
            control.read(os.path.join(debiandir, 'control'))
        else:
            env = self.get_jinja_env()
            data = env.get_template(os.path.join(debiandir, 'control.j2')).render(**self.args.vars)
            control.readfp(data.splitlines())

        version = self.get_version(module)

        # Imported package sometimes don't have the same "local tag" as ours.
        # FIXME: this code is mostly duplicated from changelog.py
        if changelog_is_up_to_date(os.path.join(debiandir, 'changelog'), version):
            line = file(os.path.join(debiandir, 'changelog'), 'r').readline()
            version = re.match('^(\w[-+0-9a-z.]*) \(([^\(\) \t]+)\)', line, re.I).group(2)

        if ':' in version:
            version = version.split(':',1)[1]
        if self.args.build_tag:
            version += self.args.build_tag

        packages = []
        for package in control.sections:
            name = package['Package']
            arch = package['Architecture']
            if arch == 'any':
                arch = self.args.arch

            packages.append('%s_%s_%s.deb' % (name, version, arch))

        return packages
