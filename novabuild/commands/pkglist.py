# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.config import ModuleSetParser

def list_packages(moduleset):
    for section in sorted(moduleset.sections()):
        items = dict(moduleset.items(section))
        items['name'] = section
        print "%(category)-18s %(name)-28s %(version)-15s %(source)s" % items

def main(moduleset, args):
    list_packages(moduleset)
