from importlib import import_module
from nose import tools
from path import path
import os
import unittest

#@! assume virtualenv usage
venv = path(os.environ.get('VIRTUAL_ENV'))


class TestGenCandidates(unittest.TestCase):
    def makeone(self, slug):
        from loadwarrior.locustext import candidates
        return [x for x in candidates(slug)]

    def test_root(self):
        out = self.makeone('/here')
        assert out  == ['/here'], out

    def test_expanded(self):
        out = self.makeone('~/here')
        assert out  == [path('~/here').expanduser()], out

    def test_implicit_filename(self):
        fn = 'filename'
        out = self.makeone(fn)
        assert out == [path('./')/fn, venv/'etc/loadwarrior'/fn, path('/etc/loadwarrior')/fn ], out





class TestSetup(unittest.TestCase):
    def test_import(self):
        lf = import_module('.locustfile', 'loadwarrior.tests')
        assert 'statsd' in lf.plugins
        assert lf.plugins.get('statsd')
        assert hasattr(lf, 'a_test')

