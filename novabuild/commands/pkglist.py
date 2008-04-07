# -*- coding: utf-8 -*- ex:set ts=4 et:

from novabuild.config import ModuleSetParser

def main(argv):
    c = ModuleSetParser(argv[0])

    for section in sorted(c.sections()):
        items = dict(c.items(section))
        items['name'] = section
        print "%(category)-18s %(name)-28s %(version)-15s %(source)s" % items
