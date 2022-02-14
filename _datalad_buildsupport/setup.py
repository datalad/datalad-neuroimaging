# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the DataLad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##


import datetime
import os

from os.path import (
    dirname,
    join as opj,
)
from setuptools import Command, DistutilsOptionError
from setuptools.config import read_configuration

import versioneer

from . import formatters as fmt


class BuildManPage(Command):
    # The BuildManPage code was originally distributed
    # under the same License of Python
    # Copyright (c) 2014 Oz Nahum Tiram  <nahumoz@gmail.com>

    description = 'Generate man page from an ArgumentParser instance.'

    user_options = [
        ('manpath=', None,
         'output path for manpages (relative paths are relative to the '
         'datalad package)'),
        ('rstpath=', None,
         'output path for RST files (relative paths are relative to the '
         'datalad package)'),
        ('parser=', None, 'module path to an ArgumentParser instance'
         '(e.g. mymod:func, where func is a method or function which return'
         'a dict with one or more arparse.ArgumentParser instances.'),
        ('cmdsuite=', None, 'module path to an extension command suite '
         '(e.g. mymod:command_suite) to limit the build to the contained '
         'commands.'),
    ]

    def initialize_options(self):
        self.manpath = opj('build', 'man')
        self.rstpath = opj('docs', 'source', 'generated', 'man')
        self.parser = 'datalad.cmdline.main:setup_parser'
        self.cmdsuite = None

    def finalize_options(self):
        if self.manpath is None:
            raise DistutilsOptionError('\'manpath\' option is required')
        if self.rstpath is None:
            raise DistutilsOptionError('\'rstpath\' option is required')
        if self.parser is None:
            raise DistutilsOptionError('\'parser\' option is required')
        mod_name, func_name = self.parser.split(':')
        fromlist = mod_name.split('.')
        try:
            mod = __import__(mod_name, fromlist=fromlist)
            self._parser = getattr(mod, func_name)(
                ['datalad'],
                formatter_class=fmt.ManPageFormatter,
                return_subparsers=True,
                # ignore extensions only for the main package to avoid pollution
                # with all extension commands that happen to be installed
                help_ignore_extensions=self.distribution.get_name() == 'datalad')

        except ImportError as err:
            raise err
        if self.cmdsuite:
            mod_name, suite_name = self.cmdsuite.split(':')
            mod = __import__(mod_name, fromlist=mod_name.split('.'))
            suite = getattr(mod, suite_name)
            self.cmdlist = [c[2] if len(c) > 2 else c[1].replace('_', '-').lower()
                            for c in suite[1]]

        self.announce('Writing man page(s) to %s' % self.manpath)
        self._today = datetime.date.today()

    @classmethod
    def handle_module(cls, mod_name, **kwargs):
        """Module specific handling.

        This particular one does
        1. Memorize (at class level) the module name of interest here
        2. Check if 'datalad.extensions' are specified for the module,
           and then analyzes them to obtain command names it provides

        If cmdline commands are found, its entries are to be used instead of
        the ones in datalad's _parser.

        Parameters
        ----------
        **kwargs:
            all the kwargs which might be provided to setuptools.setup
        """
        cls.mod_name = mod_name

        exts = kwargs.get('entry_points', {}).get('datalad.extensions', [])
        for ext in exts:
            assert '=' in ext      # should be label=module:obj
            ext_label, mod_obj = ext.split('=', 1)
            assert ':' in mod_obj  # should be module:obj
            mod, obj = mod_obj.split(':', 1)
            assert mod_name == mod  # AFAIK should be identical

            mod = __import__(mod_name)
            if hasattr(mod, obj):
                command_suite = getattr(mod, obj)
                assert len(command_suite) == 2  # as far as I see it
                if not hasattr(cls, 'cmdline_names'):
                    cls.cmdline_names = []
                cls.cmdline_names += [
                    cmd
                    for _, _, cmd, _ in command_suite[1]
                ]

    def run(self):

        dist = self.distribution
        #homepage = dist.get_url()
        #appname = self._parser.prog
        appname = 'datalad'

        cfg = read_configuration(
            opj(dirname(dirname(__file__)), 'setup.cfg'))['metadata']

        sections = {
            'Authors': """{0} is developed by {1} <{2}>.""".format(
                appname, cfg['author'], cfg['author_email']),
        }

        for cls, opath, ext in ((fmt.ManPageFormatter, self.manpath, '1'),
                                (fmt.RSTManPageFormatter, self.rstpath, 'rst')):
            if not os.path.exists(opath):
                os.makedirs(opath)
            for cmdname in getattr(self, 'cmdline_names', list(self._parser)):
                if hasattr(self, 'cmdlist') and cmdname not in self.cmdlist:
                    continue
                p = self._parser[cmdname]
                cmdname = "{0}{1}".format(
                    'datalad ' if cmdname != 'datalad' else '',
                    cmdname)
                format = cls(
                    cmdname,
                    ext_sections=sections,
                    version=versioneer.get_version())
                formatted = format.format_man_page(p)
                with open(opj(opath, '{0}.{1}'.format(
                        cmdname.replace(' ', '-'),
                        ext)),
                        'w') as f:
                    f.write(formatted)


class BuildRSTExamplesFromScripts(Command):
    description = 'Generate RST variants of example shell scripts.'

    user_options = [
        ('expath=', None, 'path to look for example scripts'),
        ('rstpath=', None, 'output path for RST files'),
    ]

    def initialize_options(self):
        self.expath = opj('docs', 'examples')
        self.rstpath = opj('docs', 'source', 'generated', 'examples')

    def finalize_options(self):
        if self.expath is None:
            raise DistutilsOptionError('\'expath\' option is required')
        if self.rstpath is None:
            raise DistutilsOptionError('\'rstpath\' option is required')
        self.announce('Converting example scripts')

    def run(self):
        opath = self.rstpath
        if not os.path.exists(opath):
            os.makedirs(opath)

        from glob import glob
        for example in glob(opj(self.expath, '*.sh')):
            exname = os.path.basename(example)[:-3]
            with open(opj(opath, '{0}.rst'.format(exname)), 'w') as out:
                fmt.cmdline_example_to_rst(
                    open(example),
                    out=out,
                    ref='_example_{0}'.format(exname))


class BuildConfigInfo(Command):
    description = 'Generate RST documentation for all config items.'

    user_options = [
        ('rstpath=', None, 'output path for RST file'),
    ]

    def initialize_options(self):
        self.rstpath = opj('docs', 'source', 'generated', 'cfginfo')

    def finalize_options(self):
        if self.rstpath is None:
            raise DistutilsOptionError('\'rstpath\' option is required')
        self.announce('Generating configuration documentation')

    def run(self):
        opath = self.rstpath
        if not os.path.exists(opath):
            os.makedirs(opath)

        from datalad.interface.common_cfg import definitions as cfgdefs
        from datalad.dochelpers import _indent

        categories = {
            'global': {},
            'local': {},
            'dataset': {},
            'misc': {}
        }
        for term, v in cfgdefs.items():
            categories[v.get('destination', 'misc')][term] = v

        for cat in categories:
            with open(opj(opath, '{}.rst.in'.format(cat)), 'w') as rst:
                rst.write('.. glossary::\n')
                for term, v in sorted(categories[cat].items(), key=lambda x: x[0]):
                    rst.write(_indent(term, '\n  '))
                    qtype, docs = v.get('ui', (None, {}))
                    desc_tmpl = '\n'
                    if 'title' in docs:
                        desc_tmpl += '{title}:\n'
                    if 'text' in docs:
                        desc_tmpl += '{text}\n'
                    if 'default' in v:
                        default = v['default']
                        if hasattr(default, 'replace'):
                            # protect against leaking specific home dirs
                            v['default'] = default.replace(os.path.expanduser('~'), '~')
                        desc_tmpl += 'Default: {default}\n'
                    if 'type' in v:
                        type_ = v['type']
                        if hasattr(type_, 'long_description'):
                            type_ = type_.long_description()
                        else:
                            type_ = type_.__name__
                        desc_tmpl += '\n[{type}]\n'
                        v['type'] = type_
                    if desc_tmpl == '\n':
                        # we need something to avoid joining terms
                        desc_tmpl += 'undocumented\n'
                    v.update(docs)
                    rst.write(_indent(desc_tmpl.format(**v), '    '))
