# -*- coding: utf-8 -*- ex:set ts=4 sw=4 et:

import sys
from exceptions import Exception

class ControlSection(dict):
    """
    A section of a Debian Control file.
    """
    def __init__(self):
        dict.__init__(self)
        self._key_order = []

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if key not in self._key_order:
            self._key_order.append(key)

    def dump(self):
        return ''.join("%s: %s\n" % (key, self[key].replace('\n', '\n  ')) for key in self._key_order) + "\n"

class BasicControlParser(object):
    section_class = ControlSection

    def __init__(self, defaults=None):
        self._sections = []
        self._defaults = {}
        if defaults:
            for key, value in defaults.items():
                self._defaults[self.optionxform(key)] = value

    def optionxform(self, option):
        return '-'.join(x.capitalize() for x in option.split('-'))

    def append_section(self, section):
        self._sections.append(section)

    def read(self, filename):
        fp = file(filename, 'r')
        self.readfp(fp)
        fp.close()

    def readfp(self, fp):
        """Read and parse a debian control file, given a file object."""

        section = None
        lastkey = None
        lineno = 0

        for line in fp:
            line = line.rstrip()
            lineno += 1
            if line == '':
                if section:
                    self.append_section(section)
                    section = None
                    lastkey = None
                continue
            
            if line[0] in ' \t':
                assert lastkey is not None
                line = line.lstrip()
                if line == '.':
                    section[lastkey] += '\n'
                else:
                    section[lastkey] += '\n' + line
                continue

            assert ':' in line
            
            key, value = [bit.strip() for bit in line.split(':', 1)]

            if not section:
                section = self.section_class()

            section[key] = value
            lastkey = key

        if section:
            self.append_section(section)

    def __getitem__(self, item):
        return self._sections[item]

    def __getslice__(self, a, b):
        return self._sections[a:b]

    def __iter__(self):
        return iter(self._sections)

    @property
    def sections(self):
        return self._sections

    def dump(self):
        return '\n'.join(section.dump() for section in self._sections)

class PackageControlParser(BasicControlParser):
    def __init__(self, defaults=None):
        BasicControlParser.__init__(self, defaults)
        self.source = None

    def append_section(self, section):
        if self.source is None:
            self.source = section
        else:
            BasicControlParser.append_section(self, section)

    def dump(self):
        return self.source.dump() + "\n" + \
               BasicControlParser.dump(self)

if __name__ == '__main__':
    c = PackageControlParser()
    c.read(sys.argv[1])
    print c.dump()
