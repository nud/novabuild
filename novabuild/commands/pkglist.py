# -*- coding: utf-8 -*- ex:set ts=4 et:

def list_packages(moduleset):
    print "Category           Package Name                 Version         Source URI"
    print "---------          -------------                --------        -----------"

    for section in sorted(moduleset.sections()):
        items = dict(moduleset.items(section))
        items['name'] = section
        print "%(category)-18s %(name)-28s %(version)-15s %(source)s" % items


def main(moduleset, args):
    list_packages(moduleset)
