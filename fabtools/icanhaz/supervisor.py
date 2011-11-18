"""
Idempotent API for managing supervisor processes
"""
from fabtools.icanhaz import deb
from fabtools.supervisor import *


def process(name, options=None, template_root=''):
    """
    I can haz supervisor process
    """
    if isinstance(name, basestring):
        name = [name]
    deb.package('supervisor')
    for n in name:
        add_process(n, options, template_root=template_root)
    reload_config()
    if process_status(name) == 'STOPPED':
        start_process(name)
