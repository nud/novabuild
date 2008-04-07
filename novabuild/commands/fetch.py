# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys
from novabuild.config import ModuleSetParser
from novabuild.run import system
from novabuild.colours import red, blue
from exceptions import Exception


def check_code(code, package):
    if code != 0:
        raise Exception("Could not fetch package %s" % package)


def fetch(moduleset, package):
    if (os.path.exists('tarballs/%s' % moduleset.get(package, 'basename'))):
        print blue("File already exists: '%s'" % moduleset.get(package, 'basename'))
        return False

    source_type = moduleset.get(package, 'source-type')

    if source_type == 'wget':
        code = system('wget -Nc %s -Otarballs/%s' % (moduleset.get(package, 'source'), moduleset.get(package, 'basename')))
        check_code(code, package)

    elif source_type == 'svn':
        tmpdir = '%s-%s' % (package, moduleset.get(package, 'orig-version'))

        print blue("Exporting the SVN snapshot")
        code = system('svn export --force %s tarballs/%s' % (moduleset.get(package, 'source'), tmpdir))
        check_code(code, package)

        print blue("Generating tarball")
        code = system('cd tarballs && tar czvf %s %s' % (moduleset.get(package, 'basename'), tmpdir))
        check_code(code, package)

        print blue("Removing temporary directory")
        code = system('rm -rf tarballs/%s' % tmpdir)
        check_code(code, package)

    elif source_type == 'local':
        filename = moduleset.get(package, 'source')
        if filename.startswith('file://'):
            filename = filename[7:]

        code = system('cp %s tarballs/' % filename)
        check_code(code, package)

    else:
        raise Exception("The '%s' source type is not handled yet" % source_type)

    return True


def main(argv):
    c = ModuleSetParser(argv[0])
    package = argv[1]

    try:
        fetch(c, package)

    except Exception, e:
        print red(e)
        sys.exit(1)
