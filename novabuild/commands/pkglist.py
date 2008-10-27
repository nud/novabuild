# -*- coding: utf-8 -*- ex:set ts=4 et:

# Function to be used with sort or sorted
# It compares two dict by looking at the specified fields in order.
def cmp_by(*fields):
    def cmpfunc(m1, m2):
        for f in fields:
            c = cmp(m1[f], m2[f])
            if c != 0: return c
        return 0
    return cmpfunc

def list_packages(moduleset):
    print "Category           Package Name                 Version         Source URI"
    print "---------          -------------                --------        -----------"

    for module in sorted(moduleset._sections.values(), cmp_by('Category', 'Module')):
        items = {
            'category': module['Category'],
            'name': module.name,
            'version': module['Version'],
            'source': module['Source'],
        }
        print "%(category)-18s %(name)-28s %(version)-15s %(source)s" % items


def main(moduleset, args):
    list_packages(moduleset)
