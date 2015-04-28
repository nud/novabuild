# -*- coding: utf-8 -*- ex:set ts=4 et:

import base
import os

from novabuild.run import system, check_code
from novabuild.colours import blue


class BuildMethod(base.BuildMethod):
    # Set up the dpkg environment for the build.
    def setup_build_env(self, module, build_dir):
        self.uncompress_tarball(module, build_dir)

        print blue("Configuring the kernel")
        code = system('cp debian/config-%s-%s %s/.config' % (module['Version'], self.args.arch, build_dir))
        check_code(code, module)

    def get_rev_tag(self, module):
        return self.args.revision_pattern % module['Build-Number']

    def build_module(self, module, build_dir):
        self.setup_build_env(module, build_dir)

        print blue("Building linux kernel '%s'" % module['Version'])
        cwd = os.path.expanduser('~/tmp-build-dir/linux-%s' % module['Version'])
        code = system('make-kpkg --revision=%s kernel_image kernel_headers kernel_source' % self.get_rev_tag(module),
                                  cwd=cwd, root=True)
        check_code(code, module)


    def list_module_packages(self, module):
        version = module['Version']
        rev_tag = self.get_rev_tag(module)
        return ["linux-headers-%s_%s_%s.deb" % (version, rev_tag, self.args.arch),
                "linux-image-%s_%s_%s.deb" % (version, rev_tag, self.args.arch),
                "linux-source-%s_%s_all.deb" % (version, rev_tag)]
