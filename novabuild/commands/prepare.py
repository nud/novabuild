# -*- coding: utf-8 -*- ex:set ts=4 et:

import os, sys
import getopt
from novabuild.run import system
from novabuild.colours import red, blue

def usage():
    print sys.argv[0] + ' [--help] [--verbose] [--distro=distro] [--name=name]'

def main(argv):
    # Get the user name.
    # Remember are supposed to be ran with sudo
    if 'SUDO_USER' in os.environ:
        user = os.environ['SUDO_USER']
    else:
        user = os.environ['USER']
    
    chroot_base = '/chroots'
    
    ########################################################################
    try:
        opts, args = getopt.getopt(argv, 'hvd:n:',
                                   ['help', 'verbose', 'distro=', 'name='])
    except getopt.GetoptError, e:
        # print help information and exit:
        print str(e) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    
    debian_mirror = 'http://ftp.be.debian.org/debian'
    distro = 'etch'
    chroot_name = None
    verbose = False
    
    for o, a in opts:
        if o in ('-v', '--verbose'):
            verbose = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif o in ('-d', '--distro'):
            distro = a
        elif o in ('-n', '--name'):
            chroot_name = a
    
    if chroot_name is None:
        chroot_name = distro
    chroot_name = user + '-' + chroot_name
    chroot_path = os.path.join(chroot_base, chroot_name)
    
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
    f.write('\n[' + chroot_name + ']\n');
    for (key, value) in config.iteritems():
        if isinstance(value, list):
            value = ','.join(value)
        elif isinstance(value, bool):
            value = value and 'true' or 'false'
        f.write('%s=%s\n' % (key, value))
    f.close()
    
    ########################################################################
    
    print blue("Installing software required for packaging")
    
    to_install = (
        'dpkg-dev',
        'debhelper',
        'kernel-package',
    )
    
    code = system('schroot -c ' + chroot_name + ' -d /root -- apt-get -y -u install ' + ' '.join(to_install))
    if code != 0:
        print red("Cound not install the base packages in the chroot.")
        sys.exit(1)

    ########################################################################
    
    print blue("Bootstraping done")
    print blue("Use 'schroot -c %s -d /root' for further access to your chroot environment." % chroot_name)
    sys.exit(0)
