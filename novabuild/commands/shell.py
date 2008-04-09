# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.chroot import Chroot
import sys

def main(argv):
    chroot = Chroot(argv[0])

    sys.exit(chroot.system('',))
