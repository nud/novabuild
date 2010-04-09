# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.chroot import Chroot
import sys

def main(chroot, args):
    is_root = '-r' in args or '--root' in args
    return chroot.system('', root = is_root)
