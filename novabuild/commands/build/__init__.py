# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys, glob, traceback
from novabuild.run import system, check_code
from novabuild.colours import red, blue
from novabuild.debcontrol import PackageControlParser
from exceptions import Exception


def get_build_method(module, args, quiet=False):
    if not quiet:
        print blue("Using build method '%s'" % module['Build-Method'])

    pymodule = __import__("novabuild.commands.build.%s" % module['Build-Method'],
                          globals(), locals(), ["BuildMethod"])
    return pymodule.BuildMethod(args)

def install_packages(packages_to_install, build_dir, module):
    if not packages_to_install:
        return

    control = PackageControlParser()
    control.read(os.path.join(build_dir, 'debian/control'))

    # Make a list of packages
    packages = [x['Package'] for x in control]

    # Make a list of dependencies we didn't build ourselves
    # FIXME: we skip the ${} for now.
    dependencies = []
    for package_info in control:
        if package_info['Package'] in packages:
            for dep in package_info.get('Depends', '').split(','):
                dep = dep.strip().split(None, 1)[0]
                if dep and not dep.startswith('$') and dep not in packages:
                    dependencies.append(dep)

    # Install said dependencies if there are any
    if dependencies:
        print blue("Installing dependencies for packages '%s'" % "', '".join(packages_to_install))
        code = system('apt-get install %s' % ' '.join(dependencies), root=True)
        check_code(code, module)

    # Install built packages
    print blue("Installing packages '%s'" % "', '".join(packages_to_install))
    dpkg_args = []
    for filename in glob.glob(os.path.join(os.path.dirname(build_dir), '*.deb')):
        if os.path.basename(filename).split('_', 1)[0] in packages_to_install:
            dpkg_args.append(filename)
    code = system("dpkg -i %s" % ' '.join(dpkg_args), root=True)
    check_code(code, module)

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

    TMP_BUILD_DIR = os.path.expanduser('~/tmp-build-dir')
    BUILD_DIR = os.path.join(TMP_BUILD_DIR, '%s-%s' % (module.name, module['Version']))

    code = system('rm -rf ' + os.path.expanduser('~/tmp-build-dir'), root=True)
    check_code(code, module)

    code = system('mkdir -p %s' % os.path.dirname(BUILD_DIR))
    check_code(code, module)

    method.build_module(module, BUILD_DIR)

    if module['Install']:
        install_packages([i.strip() for i in module['Install'].split(',')], BUILD_DIR, module)

    repo_dir = 'repository-%s' % args.moduleset.name
    if not os.path.exists(repo_dir):
        os.mkdir(repo_dir)
    code = system('mv -f %s/*.deb %s/' % (os.path.dirname(BUILD_DIR), repo_dir))
    return True


def register_build_arguments(parser, config, force=True, recursive=True, revision_pattern=True, build_tag=True):
    if force:
        parser.add_argument('-f', '--force', action='store_true',
                            help='force building even if already built')
    if recursive:
        parser.add_argument('-r', '--recursive', action='store_true',
                            help='build packages recursively')

    if revision_pattern:
        parser.add_argument('--revision-pattern', type=str,
                            help='pattern for building the build revision')

    if build_tag:
        parser.add_argument('--build-tag', type=str,
                            help='Tag to append to the build revision')

    parser.set_defaults(force=False, recursive=False, revision_pattern='%s', build_tag=None)

    if config.has_section('build'):
        parser.set_defaults(**dict(config.items('build')))


def register_arguments(parser, config):
    parser.help = 'build a single package'
    register_build_arguments(parser, config)
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
