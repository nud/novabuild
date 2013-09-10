# -*- coding: utf-8 -*- ex:set ts=4 et:

import os.path

import classic
from novabuild.run import system, check_code
from novabuild.colours import blue

IONCUBE_DIR = "/opt/ioncube"
IONCUBE4 = os.path.join(IONCUBE_DIR, "ioncube_encoder")
IONCUBE5 = os.path.join(IONCUBE_DIR, "ioncube_encoder5")
IONCUBE_ARGS = "--optimize max"

class BuildMethod(classic.BuildMethod):
    # Set up the dpkg environment for the build.
    def setup_build_env(self, debian_dir, build_dir, module):
        orig_dir = build_dir + ".original"

        self.uncompress_tarball(module, orig_dir)

        print blue("Encoding PHP files")

        try:
            php_version = int(module['PHP-Version'])
        except:
            php_version = 5

        ioncube = php_version == 5 and IONCUBE5 or IONCUBE4
        code = system('%s %s %s -o %s' % (ioncube, IONCUBE_ARGS, orig_dir, build_dir))
        check_code(code, module)

        code = system('rm -rf %s' % orig_dir)
        check_code(code, module)

        code = system('cp -r %s %s/debian' % (debian_dir, build_dir))
        check_code(code, module)
