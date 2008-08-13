# -*- coding: utf-8 -*- ex:set ts=4 et:

def list_packages(moduleset):
    print "Category           Package Name                 Version         Source URI"
    print "---------          -------------                --------        -----------"

    for module in moduleset:
        items = {
            'category': module['Category'],
            'name': module.name,
            'version': module['Version'],
            'source': module['Source'],
        }
        print "%(category)-18s %(name)-28s %(version)-15s %(source)s" % items


def main(moduleset, args):
    list_packages(moduleset)
