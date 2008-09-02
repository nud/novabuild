# -*- coding: utf-8 -*- ex:set ts=4 et:

import classic
from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code

IONCUBE = "/usr/local/bin/ioncube/ioncube_encoder5"

class BuildMethod(classic.BuildMethod):
    # Set up the dpkg environment for the build.
    def setup_build_env(self, debian_dir, build_dir, module):
        orig_dir = build_dir + ".original"

        self.uncompress_tarball(module, orig_dir)

        print blue("Encoding PHP files")

        code = system('%s --optimize max %s -o %s' % (IONCUBE, orig_dir, build_dir))
        check_code(code, module)

        code = system('rm -rf %s' % orig_dir)
        check_code(code, module)

        code = system('cp -r %s %s/debian' % (debian_dir, build_dir))
        check_code(code, module)
