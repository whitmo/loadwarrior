from . import pypath
from contextlib import contextmanager
from logging import getLogger
from path import path
import os
import yaml

logger = getLogger(__name__)


def candidates(filename):
    """
    A generator of possible pathes for a file to exist in config
    """
    if filename.startwith('/'):
        yield filename
        raise StopIteration
    if filename.startswith('~/'):
        yield path(filename).expanduser()
        raise StopIteration
    yield path('./') / filename
    venv = os.environ.get('VIRTUAL_ENV', None)
    if venv:
        yield path(venv) / 'etc'  / filename
    yield path('/etc') / filename


def find_config(filename, candidates=candidates, raise_error=True, logger=logger):
    """
    Iterate over possible paths, return the first one that exists

    Raise or log error if no path is found
    """
    notfound = []
    for candidate in candidates(filename):
        if candidate.exists():
            return candidate
        notfound.append(candidate)
    nf = ",".join(notfound)
    msg = "%s not found in %s"
    if raise_error:
        raise ValueError("%s not found in %s" %nf)
    logger.error(msg, nf)
    return None


def setup(name, conffile='locust.yml'):
    """
    composes the 'locustfile' from configuration
    """
    with open(find_config(conffile)) as stream:
        locust_data = yaml.load(stream)
        
    with sysimport() as sys:
        module = sys.modules[name]
        load_loci(mod, locust_data.pop('loci'))


@contextmanager
def sysimport():
    try:
        import sys
        yield sys
    finally:
        del sys
