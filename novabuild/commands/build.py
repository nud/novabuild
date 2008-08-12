# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys, glob
from novabuild.config import ModuleSetParser
from novabuild.debcontrol import PackageControlParser
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild.chroot import Chroot
from exceptions import Exception
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


def check_code(code, package):
    if code != 0:
        raise Exception("Could not build package %s" % package)


def get_dependencies(chroot, BUILD_DIR):
    control = PackageControlParser()
    control.read(os.path.join(BUILD_DIR, 'debian/control'))
    dependencies = control.source.get('Build-Depends', '')
    return [i.strip().split(None, 1)[0] for i in dependencies.split(',')]

def build(chroot, moduleset, package):
    TARBALL = os.path.join('tarballs', moduleset.get(package, 'basename'))

    if not os.path.exists(TARBALL):
        raise Exception("You must fetch the package '%s' before building it." % package)

    BUILD_ROOT = os.path.join(chroot.get_home_dir(), 'tmp-build-dir')
    BUILD_DIR = os.path.join (BUILD_ROOT, '%s-%s' % (package, moduleset.get(package, 'version')))
    DEBIAN_DIR = os.path.join('debian', 'debian-%s' % package)

    print blue("Uncompressing '%s'" % TARBALL)

    code = chroot.system('rm -rf /home/%s/tmp-build-dir' % chroot.user, root=True)
    check_code(code, package)

    code = system('mkdir -p %s' % BUILD_ROOT)
    check_code(code, package)

    if TARBALL.endswith('.tar.bz2'):
        code = system('tar xjf %s -C %s' % (TARBALL, BUILD_ROOT))
        check_code(code, package)
    elif TARBALL.endswith('.tar.gz') or TARBALL.endswith('.tgz'):
        code = system('tar xzf %s -C %s' % (TARBALL, BUILD_ROOT))
        check_code(code, package)
    elif TARBALL.endswith('.zip'):
        code = system('unzip %s -d %s' % (TARBALL, BUILD_ROOT))
        check_code(code, package)
    else:
        raise Exception("Cannot find the type of the archive.")


    # Kernel packages have to be handled specially.
    if package == 'linux':
        print blue("Building '%s' '%s'" % (package, moduleset.get(package, 'version')))
        code = system('cp debian/config-%s-i386 %s/.config' % (moduleset.get(package, 'version'), BUILD_DIR))
        check_code(code, package)

        code = chroot.system('make-kpkg --revision=novacom.i386.3.0 kernel_image kernel_headers kernel_source',
                             cwd=chroot.abspath('~/tmp-build-dir/linux-%s' % moduleset.get(package, 'version')), root=True)
        check_code(code, package)

    else:
        code = system('mv %s/* %s' % (BUILD_ROOT, BUILD_DIR))
        #check_code(code, package)  FIXME: we don't want to fail when "cannot move to itself"

        code = system('cp -r %s %s/debian' % (DEBIAN_DIR, BUILD_DIR))
        check_code(code, package)

        print blue('Installing dependencies')
        code = chroot.system('apt-get install %s' % ' '.join(get_dependencies(chroot, BUILD_DIR)), root=True)
        check_code(code, package)

        # Write a new changelog entry...
        version = "%s-novacom.%s" % (moduleset.get(package, 'version'), moduleset.get(package, 'buildnumber'))
        changelog_file = "%s/debian/changelog" % BUILD_DIR

        if not changelog_is_up_to_date(changelog_file, version):
            print blue("Update ChangeLog")
            old_file = "%s/changelog" % DEBIAN_DIR
            prepend_changelog_entry(changelog_file, old_file, package, version, "* New build.")

            # backup the new changelog file
            code = system('cp -f %s %s' % (changelog_file, old_file))
            check_code (code, package)

        print blue("Building '%s' '%s'" % (package, moduleset.get(package, 'version')))
        code = chroot.system('dpkg-buildpackage', root=True, cwd='/home/%s/tmp-build-dir/%s-%s'
                             % (chroot.user, package, moduleset.get(package, 'version')))
        check_code(code, package)

        packages_to_install = [i.strip() for i in moduleset.get(package, 'install').split(',')]
        if packages_to_install != []:
            print blue("Installing packages '%s'" % "', '".join(packages_to_install))
            packages = [os.path.basename(i) for i in glob.glob(chroot.abspath('~/tmp-build-dir/*.deb', internal=False))]
            for package in packages:
                if package.split('_',1)[0] in packages_to_install:
                    code = chroot.system("dpkg -i ~/tmp-build-dir/%s" % package)
                    check_code(code, package)

    code = system('mv -f %s/*.deb repository/' % BUILD_ROOT)


def main(chroot, moduleset, args):
    package = args[0]

    try:
        build(chroot, moduleset, package)

    except Exception, e:
        print red(e)
        sys.exit(1)
