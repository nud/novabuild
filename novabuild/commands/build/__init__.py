# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys, glob
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild.misc import check_code
from exceptions import Exception


def get_build_method(module, chroot, moduleset, quiet=False):
    if not quiet:
        print blue("Using build method '%s'" % module['Build-Method'])

    pymodule = __import__("novabuild.commands.build.%s" % module['Build-Method'],
                          globals(), locals(), ["BuildMethod"])
    return pymodule.BuildMethod(chroot, moduleset)


def build(chroot, moduleset, module, force=False, recursive=False):
    method = get_build_method(module, chroot, moduleset)
    if not force and method.module_is_built(module):
        print blue("Module '%s' has already been built" % module.name)
        return False

    if recursive:
        dependencies = [x for x in [i.strip() for i in module['Depends'].split(',')] if x]
        if dependencies:
            print blue("Building dependencies for '%s'" % module.name)
            for i in dependencies:
                build(chroot, moduleset, moduleset[i], force, recursive)

    BUILD_DIR = os.path.join(chroot.get_home_dir(), 'tmp-build-dir',
                             '%s-%s' % (module.name, module['Version']))

    code = chroot.system('rm -rf /home/%s/tmp-build-dir' % chroot.user, root=True)
    check_code(code, module)

    code = system('mkdir -p %s' % os.path.dirname(BUILD_DIR))
    check_code(code, module)

    method.build_module(module, BUILD_DIR)

    if module['Install']:
        packages_to_install = [i.strip() for i in module['Install'].split(',')]
        if packages_to_install != []:
            print blue("Installing packages '%s'" % "', '".join(packages_to_install))
            packages = [os.path.basename(i) for i in glob.glob(chroot.abspath('~/tmp-build-dir/*.deb', internal=False))]
            packages = [chroot.abspath('~/tmp-build-dir/%s' % package) for package in packages
                                                     if package.split('_', 1)[0] in packages_to_install]
            code = chroot.system("dpkg -i %s" % ' '.join(packages), root=True)
            check_code(code, module)

    repo_dir = 'repository-%s' % chroot.name
    if not os.path.exists(repo_dir):
        os.mkdir(repo_dir)
    code = system('mv -f %s/*.deb %s/' % (os.path.dirname(BUILD_DIR), repo_dir))
    return True


def main(chroot, moduleset, args):
    try:
        force = '-f' in args or '--force' in args
        recursive = '-r' in args or '--recursive' in args
        for arg in [x for x in args if not x.startswith('-')]:
            module = moduleset[arg]
            build(chroot, moduleset, module, force=force, recursive=recursive)

    except Exception, e:
        print red(e)
        sys.exit(1)
