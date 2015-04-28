# -*- coding: utf-8 -*- ex:set ts=4 sw=4 et:

import os, sys
import getopt
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild import env


def register_arguments(parser, config):
    parser.description = 'Prepare the virtual machine'

    if config.has_section('prepare'):
        parser.set_defaults(**dict(config.items('prepare')))


def main(args):
    # Get the user name.
    # Remember we are supposed to be ran with sudo
    user = env.get_user_name()
    uid = env.get_uid()

    if not user or not uid:
        print "You should run 'novabuild prepare' using sudo."
        return 1

    ########################################################################

    print blue("Configuring APT")

    # Here we save a custom APT configuration, for a space-saving non-interactive
    # apt-get.

    f = file('/etc/apt/apt.conf.d/95novabuild', 'w')
    f.write("""
    APT::Get::Assume-Yes "true";
    APT::Get::AllowUnauthenticated "true";
    APT::Get::Clean "always";
    APT::Install-Recommends "false";
    """)
    f.close()

    ########################################################################

    print blue("Configuring sudo")

    f = file('/etc/sudoers.d/95novabuild', 'w')
    f.write("%s    ALL = NOPASSWD: ALL" % user)
    f.close()

    os.chmod('/etc/sudoers.d/95novabuild', 0440)

    ########################################################################

    print blue("Installing software required for packaging")

    # What packages should we install?
    to_install = (
        'dpkg-dev',
        'debhelper',
        'dpatch',
        'kernel-package',
        'fakeroot',
        'bzip2',
        'dialog',
        'vim',
    )

    code = system('apt-get install ' + ' '.join(to_install), root=True)
    if code != 0:
        print red("Could not install additional packages")
        return 1

    ########################################################################

    print blue("Bootstraping done")
    return 0
