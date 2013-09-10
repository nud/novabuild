# -*- coding: utf-8 -*- ex:set ts=4 sw=4 et:

import os, sys
import getopt
from novabuild.run import system
from novabuild.colours import red, blue
from novabuild import env


def register_arguments(parser, config):
    parser.description = 'Prepare a chroot'
    parser.add_argument('-d', '--distro', dest='distro', default='squeeze', help='distribution to install')

    if config.has_section('prepare'):
        parser.set_defaults(**dict(config.items('prepare')))


def main(args):
    chroot_base = '/chroots'
    debian_mirror = 'http://ftp.debian.org/debian'

    chroot = args.chroot
    distro = args.distro
    arch = args.arch

    # Get the user name.
    # Remember we are supposed to be ran with sudo
    user = env.get_user_name()
    uid = env.get_uid()

    if not user or not uid:
        usage()
        return 1

    chroot_path = os.path.join(chroot_base, user + '-' + chroot.name)
    
    ########################################################################

    if not os.path.exists(chroot_path):
        print blue("Setup the chroot in '%s'" % chroot_path)

        code = system('debootstrap --variant=buildd --arch=%s %s %s %s' % (arch, distro, chroot_path, debian_mirror))
        if code != 0:
             print red("Cound not bootstrap the chroot.")
             return 1

    ########################################################################

    print blue("Ensure the /root directory exists")
    code = system('mkdir -p %s' % chroot.abspath('/root', internal=False))

    ########################################################################
    
    print blue("Configuring APT")

    # Here we save a custom APT configuration in the chroot, for a
    # space-saving non-interactive apt-get.

    f = file(os.path.join(chroot_path, 'etc/apt/apt.conf.d/95novabuild'), 'w')
    f.write("""
    APT::Get::Assume-Yes "true";
    APT::Get::AllowUnauthenticated "true";
    APT::Get::Clean "always";
    APT::Install-Recommends "false";
    """)
    f.close()
    
    ########################################################################
    
    print blue("Adding the new chroot into schroot config")

    # The actual configuration.
    config = {
        'type': 'directory',
        'directory': chroot_path,
        'description': 'Debian %s for user %s' % (distro.capitalize(), user),
        'groups': 'root',
        'root-groups': 'root',
        'users': ['root', user],
        'root-users': ['root', user],
    }
    
    # Dump the configuration into schroot.conf
    f = file('/etc/schroot/schroot.conf', 'a')
    f.write('\n[%s-%s]\n' % (user, chroot.name))
    for (key, value) in config.iteritems():
        if isinstance(value, list):
            value = ','.join(value)
        elif isinstance(value, bool):
            value = value and 'true' or 'false'
        f.write('%s=%s\n' % (key, value))
    f.close()

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

    chroot.start_session()
    code = chroot.system('apt-get install ' + ' '.join(to_install), root=True)
    if code != 0:
        print red("Could not install additional packages")
        return 1

    ########################################################################

    print blue("Bootstraping done")
    print blue("Use 'schroot -c %s-%s -d %s' for further access to your chroot environment."
                % (user, chroot.name, chroot.get_home_dir()))
    return 0
