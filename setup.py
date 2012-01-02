#!/usr/bin/env python
# -*- coding: utf-8 -*- ex:set sw=4 ts=4 et:

from distutils.core import setup

setup(name='novabuild',
      version='0.1',
      description='Automatic Package Builder',
      author='Steve Frécinaux',
      author_email='sfrecinaux@beip.be',
      url='http://www.beip.be/',
      packages=['novabuild',
                'novabuild.commands',
                'novabuild.commands.build'],
      scripts=['bin/novabuild'],
)
