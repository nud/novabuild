# -*- coding: utf-8 -*- ex:set ts=4 et:

import os
import re
from debcontrol import BasicControlParser, ControlSection

class Module(ControlSection):
    protocols = {
        'svn': ('svn', 'svn+ssh'),
        'wget': ('http', 'https', 'ftp'),
        'local': ('file', ),
    }
    defaults = {
        'Download-Dir': '/tmp',
        'Version': '1.0.0',
        'Orig-Version': '%(version)s',
        'Category': 'std',
        'Changelog': '',
        'Depend': '',
        'Install': 'no',
        'Encode': 'no',
        'Build-Number': '1',
    }

    VALUES_PATTERN = re.compile(r'\${([^}]+)}')
    def _expand_values(self, value):
        def callback(m):
            return self[m.group(1)]
        return self.VALUES_PATTERN.sub(callback, value)

    def __getitem__(self, key):
        try:
            return self._expand_values(dict.__getitem__(self, key))
        except KeyError, e:
            if key == 'Basename':
                if self['Source-Type'] == 'svn':
                    return '%s-%s.tar.gz' % (self['Module'], self['Orig-Version'])
                else:
                    return os.path.basename(self['Source'])
            elif key == 'Source-Type':
                source = self['Source']
                for x, l in self.protocols.items():
                    for p in l:
                        if source.startswith(p + ':'):
                            return x
                return 'unknown'
            elif key in self.defaults:
                return self._expand_values(self.defaults[key])
            else:
                raise e

    @property
    def name(self):
        return self['Module']


class ModuleSet(BasicControlParser):
    section_class = Module

    def __init__(self, moduleset):
        BasicControlParser.__init__(self)
        self._sections = {}
        self.read(os.path.join('modulesets', moduleset))

    def append_section(self, section):
        self._sections[section['Module']] = section
