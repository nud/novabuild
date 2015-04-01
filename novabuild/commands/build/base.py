# -*- coding: utf-8 -*- ex:set ts=4 et:

from exceptions import NotImplementedError

import os
from novabuild.run import system, check_code
from novabuild.colours import blue
from novabuild.commands.fetch import fetch

class BuildMethod(object):
    def __init__(self, args):
        self.args = args

    # Uncompress the module tarball
    def uncompress_tarball(self, module, destination):
        filename = os.path.join('tarballs', module['Basename'])
        if not os.path.exists(filename):
            fetch(module)

        dest_parent = os.path.dirname(destination)

        print blue("Uncompressing '%s'" % filename)
        if filename.endswith('.tar.bz2') or filename.endswith('.tbz'):
            check_code(system('tar xjf %s -C %s' % (filename, dest_parent)), module)
        elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
            check_code(system('tar xzf %s -C %s' % (filename, dest_parent)), module)
        elif filename.endswith('.zip'):
            check_code(system('unzip %s -d %s' % (filename, dest_parent)), module)
        else:
            raise Exception("Cannot find the type of the archive.")

        # Put the directory in the tarball in the right directory
        if not os.path.exists(destination):
            contents = os.listdir(dest_parent)
            if len(contents) == 1 and os.path.isdir(contents[0]):
                check_code(system('mv "%s/%s" %s' % (dest_parent, contents[0], destination)), module)
            else:
                check_code(system('mkdir %s' % destination), module)
                files = [os.path.join(dest_parent, file) for file in contents]
                check_code(system('mv %s %s' % (' '.join(files), destination)), module)

    def build_module(self, module, build_dir):
        raise NotImplementedError('You must implement the build_module method')

    def list_module_packages(self, module):
        raise NotImplementedError('You must implement the list_module_packages method')

    def module_is_built(self, module):
        for package in self.list_module_packages(module):
            if not os.path.exists(os.path.join('repository-' + self.args.chroot.name, package)):
                return False
        return True
