# -*- coding: utf-8 -*- ex:set ts=4 et:

from build import get_build_method

# Function to be used with sort or sorted
# It compares two dict by looking at the specified fields in order.
def cmp_by(*fields):
    def cmpfunc(m1, m2):
        for f in fields:
            c = cmp(m1[f], m2[f])
            if c != 0: return c
        return 0
    return cmpfunc

def list_packages(moduleset, chroot=None):
    print "B Package Name                 Version         Category           Source URI"
    print "- -------------                --------        ---------          -----------"

    for module in sorted(moduleset._sections.values(), cmp_by('Category', 'Module')):
        items = {
            'category': module['Category'],
            'name': module.name,
            'version': module['Version'],
            'source': module['Source'],
            'built': ' ',
        }
        if chroot is not None:
            method = get_build_method(module, chroot, moduleset, quiet=True)
            if method.module_is_built(module):
                items['built'] = '#'


        print "%(built)-1s %(name)-28s %(version)-15s %(category)-18s %(source)s" % items


def register_arguments(parser):
    parser.description = 'List the packages'


def main(args):
    list_packages(args.moduleset, args.chroot)
