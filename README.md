Novabuild
==========

Novabuild is a build system used by [Be IP][1] to generate Debian (.deb)
packages out of upstream tarballs or repositories and a separate repository
of 'debian/' directories.

Installation and dependencies
-----------------------------

To use Novabuild you first need to install the following dependencies:

  * python-argparse
  * python-jinja2
  * schroot
  * sudo

Then, install this package:

    $ python setup.py install

Preparing the chroot
--------------------

From within your novabuild repository, start preparing the chroot:

    $ sudo novabuild prepare

Once this is done, you can build your package:

    $ novabuild build $package_name

See `novabuild --help` for more information.

  [1]: http://www.beip.be
