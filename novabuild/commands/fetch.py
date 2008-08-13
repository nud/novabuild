# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys
from novabuild.run import system
from novabuild.colours import red, blue
from exceptions import Exception


def check_code(code, module):
    if code != 0:
        raise Exception("Could not fetch module %s" % module.name)


def fetch(module):
    if (os.path.exists('tarballs/%s' % module['Basename'])):
        print blue("File already exists: '%s'" % module['Basename'])
        return False

    source_type = module['Source-Type']

    if source_type == 'wget':
        code = system('wget -Nc %s -Otarballs/%s' % (module['Source'], module['Basename']))
        check_code(code, module)

    elif source_type == 'svn':
        tmpdir = '%s-%s' % (module.name, module['Orig-Version'])

        print blue("Exporting the SVN snapshot")
        code = system('svn export --force %s tarballs/%s' % (module['Source'], tmpdir))
        check_code(code, module)

        print blue("Generating tarball")
        code = system('cd tarballs && tar czvf %s %s' % (module['Basename'], tmpdir))
        check_code(code, module)

        print blue("Removing temporary directory")
        code = system('rm -rf tarballs/%s' % tmpdir)
        check_code(code, module)

    elif source_type == 'local':
        filename = module['Source']
        if filename.startswith('file://'):
            filename = filename[7:]

        code = system('cp %s tarballs/' % filename)
        check_code(code, module)

    else:
        raise Exception("The '%s' source type is not handled yet" % source_type)

    return True


def main(moduleset, args):
    module = moduleset[args[0]]
    try:
        fetch(module)
    except Exception, e:
        print red(e)
        sys.exit(1)
