# -*- coding: utf-8 -*- ex:set ts=4 sw=4 et:

import os, sys
import getopt
from novabuild.run import system
from novabuild.colours import red, blue
import novabuild.env as env

def usage():
    print sys.argv[0] + ' [--help] [--verbose] [--distro=distro] [--name=name]'

def main(chroot, args):
    # Get the user name.
    # Remember are supposed to be ran with sudo
    user = env.get_user_name()
    uid = env.get_uid()

    chroot_base = '/chroots'
    
    ########################################################################

    try:
        opts, args = getopt.getopt(args, 'hvd:n:',
                                   ['help', 'verbose', 'distro=', 'name='])
    except getopt.GetoptError, e:
        # print help information and exit:
        print str(e) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    
    debian_mirror = 'http://ftp.be.debian.org/debian'
    distro = 'etch'
    verbose = False
    
    for o, a in opts:
        if o in ('-v', '--verbose'):
            verbose = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o in ('-d', '--distro'):
            distro = a

    chroot_path = os.path.join(chroot_base, user + '-' + chroot.name)
    
    if os.path.exists(chroot_path):
        print blue("Directory '%s' already exists!" % chroot_path)
        sys.exit(0)
    
    ########################################################################
    
    print blue("Setup the chroot in '%s'" % chroot_path)

    code = system('debootstrap --variant=buildd %s %s %s' % (distro, chroot_path, debian_mirror))
    if code != 0:
         print red("Cound not bootstrap the chroot.")
         sys.exit(1)

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
        'type': 'plain',
        'location': chroot_path,
        'description': 'Debian %s for user %s' % (distro.capitalize(), user),
        'priority': 3,
        'groups': 'root',
        'root-groups': 'root',
        'users': ['root', user],
        'root-users': ['root', user],
        'run-setup-scripts': True,
        'run-exec-scripts': True,
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

    print blue("Create home directory for user '%s'" % user)
    code = chroot.system('mkdir /home/%s' % user, root=True)
    if code != 0:
        print red("Could not create the home directory")
        sys.exit(1)

    code = chroot.system('chown %s:%s /home/%s' % (user, user, user), root=True)
    if code != 0:
        print red("Could not set the home directory ownership")
        sys.exit(1)

    ########################################################################

    print blue("Installing software required for packaging")

    # What packages should we install?
    to_install = (
        'dpkg-dev',
        'debhelper',
        'kernel-package',
    )

    code = chroot.system('apt-get -y -u install ' + ' '.join(to_install), root=True)
    if code != 0:
        print red("Could not install additional packages")
        sys.exit(1)

    ########################################################################

    print blue("Bootstraping done")
    print blue("Use 'schroot -c %s-%s -d /home/%s' for further access to your chroot environment."
                % (user, chroot.name, user))
    sys.exit(0)
