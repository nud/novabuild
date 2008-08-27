# -*- coding: utf-8 -*- ex:set ts=4 et:

from exceptions import NotImplementedError

from novabuild.run import system
from novabuild.colours import blue
from novabuild.misc import check_code

class BuildMethod(object):
    def __init__(self, chroot, moduleset):
        self.chroot = chroot
        self.moduleset = moduleset

    def build_module(self, module, build_dir):
        raise NotImplementedError('You must implement the build_module method')
