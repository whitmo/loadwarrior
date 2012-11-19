from . import pypath
from contextlib import contextmanager
from logging import getLogger
from path import path
import os
import yaml
from . import utils

logger = getLogger(__name__)


def candidates(filename, userland='etc/loadwarrior'):
    """
    A generator of possible pathes for a file to exist in config
    """
    if filename.startswith('/'):
        yield filename
        raise StopIteration
    if filename.startswith('~/'):
        yield path(filename).expanduser()
        raise StopIteration
    yield path('./') / filename
    venv = os.environ.get('VIRTUAL_ENV', None)
    if venv:
        yield path(venv) / userland / filename
    yield path('/') / userland / filename


def setup(name, conffile='locust.yml'):
    """
    composes the 'locustfile' from configuration
    """
    conffile = utils.find_config(conffile, candidates=candidates, logger=logger)
    with open(conffile) as stream:
        locust_data = yaml.load(stream)
        
    with sysimport() as sys:
        module = sys.modules[name]
        [setattr(module, name, pypath.resolve(spec)) \
         for name, spec in locust_data.pop('loci').items()]

    plugins = module.plugins = {}
    for name, spec in locust_data.items():
        if spec.has_key('setup'):
            factory = pypath.resolve(spec.pop('setup'))
            plugins[name] = factory(**spec)


@contextmanager
def sysimport():
    try:
        import sys
        yield sys
    finally:
        del sys
