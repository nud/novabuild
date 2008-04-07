# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys
from novabuild.config import ModuleSetParser
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild.chroot import Chroot
from exceptions import Exception


def check_code(code, package):
    if code != 0:
        raise Exception("Could not build package %s" % package)


def build(chroot, moduleset, package):
    TARBALL = os.path.join('tarballs', moduleset.get(package, 'basename'))

    if not os.path.exists(TARBALL):
        raise Exception("You must fetch the package '%s' before building it." % package)

    print blue("Building '%s' '%s'" % (package, moduleset.get(package, 'version')))

    BUILD_ROOT = os.path.join(chroot.get_home_dir(), 'tmp-build-dir')
    BUILD_DIR = os.path.join (BUILD_ROOT, '%s-%s' % (package, moduleset.get(package, 'version')))
    DEBIAN_DIR = os.path.join('debian', 'debian-%s' % package)

    code = system('rm -rf %s' % BUILD_ROOT)
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
        code = system('cp %s/config-%s-i386 %s/.config' % (DEBIAN_DIR, moduleset.get(package, 'version'), BUILD_DIR))
        check_code(code, package)

        code = chroot.system('make-kpkg --revision=novacom.i386.3.0 kernel_image kernel_headers kernel_source', cwd='/root/tmp-build-dir')
        check_code(code, package)

    else:
        code = system('mv %s/* %s' % (BUILD_ROOT, BUILD_DIR))
        check_code(code, package)

        code = system('cp -r %s %s/debian' % (DEBIAN_DIR, BUILD_DIR))
        check_code(code, package)

#       cat \$(DEBIAN_DIR)/changelog-$pack_lowercase.txt > /tmp/changelog.tmp;
#       @(if [ \`cmp /tmp/changelog.tmp \$(DEB_BUILD_DIR)/$build_dirname/debian/changelog 2>&1 | grep "line 1" | wc -l\` -eq '1' ]; then
#           echo -e "\n -- Novacom Support <support@novacom.be>  \`date -R\` \n" >> /tmp/changelog.tmp;
#           cat \$(DEB_BUILD_DIR)/$build_dirname/debian/changelog >> /tmp/changelog.tmp;
#           cp /tmp/changelog.tmp \$(DEB_BUILD_DIR)/$build_dirname/debian/changelog;
#           cp /tmp/changelog.tmp \$(DEBIAN_DIR)/debian-$pack_lowercase/changelog;
#       fi;)

        code = chroot.system('dpkg-buildpackage', cwd='/root/tmp-build-dir/%s-%s' % (package, moduleset.get(package, 'version')))
        check_code(code, package)

    code = system('mv %s/*.deb repository/' % BUILD_ROOT)


def main(argv):
    chroot = Chroot(argv[0])
    c = ModuleSetParser(argv[1])
    package = argv[2]

    try:
        build(chroot, c, package)

    except Exception, e:
        print red(e)
        sys.exit(1)
