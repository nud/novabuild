# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys, glob, traceback
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild.misc import check_code
from exceptions import Exception


def get_build_method(module, args, quiet=False):
    if not quiet:
        print blue("Using build method '%s'" % module['Build-Method'])

    pymodule = __import__("novabuild.commands.build.%s" % module['Build-Method'],
                          globals(), locals(), ["BuildMethod"])
    return pymodule.BuildMethod(args)


def build(module, args):
    method = get_build_method(module, args)
    if not args.force and method.module_is_built(module):
        print blue("Module '%s' has already been built" % module.name)
        return False

    if args.recursive:
        dependencies = [x for x in [i.strip() for i in module['Depends'].split(',')] if x]
        if dependencies:
            print blue("Building dependencies for '%s'" % module.name)
            for i in dependencies:
                build(args.moduleset[i], args)

    BUILD_DIR = os.path.join(args.chroot.get_home_dir(), 'tmp-build-dir',
                             '%s-%s' % (module.name, module['Version']))

    code = args.chroot.system('rm -rf /home/%s/tmp-build-dir' % args.chroot.user, root=True)
    check_code(code, module)

    code = system('mkdir -p %s' % os.path.dirname(BUILD_DIR))
    check_code(code, module)

    method.build_module(module, BUILD_DIR)

    if module['Install']:
        packages_to_install = [i.strip() for i in module['Install'].split(',')]
        if packages_to_install != []:
            print blue("Installing packages '%s'" % "', '".join(packages_to_install))
            packages = [os.path.basename(i) for i in glob.glob(args.chroot.abspath('~/tmp-build-dir/*.deb', internal=False))]
            packages = [args.chroot.abspath('~/tmp-build-dir/%s' % package) for package in packages
                                                     if package.split('_', 1)[0] in packages_to_install]
            code = args.chroot.system("dpkg -i %s" % ' '.join(packages), root=True)
            check_code(code, module)

    repo_dir = 'repository-%s' % args.chroot.name
    if not os.path.exists(repo_dir):
        os.mkdir(repo_dir)
    code = system('mv -f %s/*.deb %s/' % (os.path.dirname(BUILD_DIR), repo_dir))
    return True


def register_build_arguments(parser, force=True, recursive=True, revision_pattern=True):
    if force:
        parser.add_argument('-f', '--force', action='store_true',
                            help='force building even if already built')
    if recursive:
        parser.add_argument('-r', '--recursive', action='store_true',
                            help='build packages recursively')

    if revision_pattern:
        parser.add_argument('--revision-pattern', type=str,
                            help='pattern for building the build revision')

    parser.set_defaults(force=False, recursive=False, revision_pattern='%s')


def register_arguments(parser):
    parser.help = 'build a single package'
    register_build_arguments(parser)
    parser.add_argument('packages', type=str, nargs='+', metavar='package',
                        help='package to build')


def main(args):
    try:
        for package in args.packages:
            build(args.moduleset[package], args)
        return 0

    except Exception, e:
        traceback.print_exc()
        return 1
