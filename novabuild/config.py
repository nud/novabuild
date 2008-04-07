# -*- coding: utf-8 -*- ex:set ts=4 et:

from ConfigParser import ConfigParser, NoOptionError
import os

class ModuleSetParser(ConfigParser):
    """
    Parse module sets and complete their configuration.
    """

    def __init__(self, moduleset, user_defaults = None):
        defaults = {
            'download-dir': '/tmp',
            'version': '1.0.0',
            'orig-version': '%(version)s',
            'category': 'std',
            'changelog': '',
            'depend': '',
            'install': 'no',
            'encode': 'no',
        }

        if user_defaults is not None:
            defaults.update(user_defaults)

        ConfigParser.__init__(self, defaults)
        self.read([os.path.join('modulesets', moduleset)])

    def get(self, section, option, raw=0, vars=None):
        try:
            return ConfigParser.get(self, section, option, raw, vars)
        except NoOptionError, e:
            if option == 'name':
                return section
            elif option == 'basename':
                if self.get(section, 'source-type') == 'svn':
                    return section + '-' + self.get(section, 'orig-version') + '.tar.gz'
                else:
                    return os.path.basename(self.get(section, 'source'))
            elif option == 'source-type':
                source = self.get(section, 'source')
                protocols = {
                    'svn': ('svn', 'svn+ssh'),
                    'wget': ('http', 'https', 'ftp'),
                    'local': ('file', ),
                }
                for x, l in protocols.iteritems():
                    for p in l:
                        if source.startswith('%s:' % p):
                            return x
                return 'unknown'
            else:
                raise e

    def items(self, section):
        l = dict(ConfigParser.items(self, section))

        # add our home-grown items
        for i in ('name', 'basename', 'source-type'):
            if i not in l:
                l[i] = self.get(section, i)

        # reformat the output so it doesn't look like we changed anything
        return sorted(l.items())

    def getboolean(self, section, option):
        v = self.get(section, option)
        if val.lower() in ('yes', 'true', '1'):
            return True
        elif val.lower() in ('no', 'false', '0'):
            return False
        else:
            raise ValueError, 'Not a boolean: %s' % v

    def dump(self):
        for section in self.sections():
            print '[%s]' % section
            for key, value in self.items(section):
                print "%s = %s" % (key, str(value))
            print
