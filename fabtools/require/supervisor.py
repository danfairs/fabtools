"""
Idempotent API for managing supervisor processes
"""
from fabtools.require import deb
from fabtools.require.files import template_file
from fabtools.supervisor import *


DEFAULT_TEMPLATE = """\
[program:%(name)s]
command=%(command)s
directory=%(directory)s
user=%(user)s
autostart=true
autorestart=true
redirect_stderr=true
"""


def _process(name, template_contents=None, template_source=None, **kwargs):
    config_filename = '/etc/supervisor/conf.d/%s.conf' % name

    context = {}
    context.update(kwargs)
    context['name'] = name

    if (template_contents is None) and (template_source is None):
        template_contents = DEFAULT_TEMPLATE

    template_file(config_filename, template_contents, template_source, context,
        use_sudo=True)


def process(name, template_contents=None, template_source=None, **kwargs):
    """
    Require a supervisor process
    """
    kw = {
        'template_contents': template_contents,
        'template_source': template_source,
    }
    kw.update(kwargs)
    processes([(name, kw)])


def processes(process_infos):
    """
    Require a number of supervisor processes.

      processes(
        ('foo', {'template_source': 'bar'}),
        ('quux', {'template_source': 'baz'}),
    )

    Supervisor takes a small amount of time to reload its configuration.
    Calling process() repeatedly may therefore fail, if supervisor is still
    reloading when subsequent calls are made. processes() allows a number of
    processes to be configured with a single configuration reload.
    """
    deb.package('supervisor')

    names = []
    for info in process_infos:
        try:
            name, kwargs = info
        except ValueError:
            name = info
            kwargs = {}
        _process(name, **kwargs)
        names.append(name)

    reload_config()
    for name in names:
        if process_status(name) == 'STOPPED':
            start_process(name)
