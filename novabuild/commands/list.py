# -*- coding: utf-8 -*- ex:set ts=4 et:

from build import get_build_method, register_build_arguments

# Function to be used with sort or sorted
# It compares two dict by looking at the specified fields in order.
def cmp_by(*fields):
    def cmpfunc(m1, m2):
        for f in fields:
            c = cmp(m1[f], m2[f])
            if c != 0: return c
        return 0
    return cmpfunc


def register_arguments(parser, config):
    parser.description = 'List the packages'
    register_build_arguments(parser, config, force=False, recursive=False)


def main(args):
    print "B Package Name                 Version         Category           Source URI"
    print "- -------------                --------        ---------          -----------"

    for module in sorted(args.moduleset._sections.values(), cmp_by('Category', 'Module')):
        items = {
            'category': module['Category'],
            'name': module.name,
            'version': module['Version'],
            'source': module['Source'],
            'built': ' ',
        }
        if args.chroot is not None:
            method = get_build_method(module, args, quiet=True)
            try:
                if method.module_is_built(module):
                    items['built'] = '#'
            except:
                pass


        print "%(built)-1s %(name)-28s %(version)-15s %(category)-18s %(source)s" % items
