import unittest
import os
from path import path
from nose import tools

#@@ we assume virtualenv usage
venv = path(os.environ.get('VIRTUAL_ENV'))

class TestGenCandidates(unittest.TestCase):
    def makeone(self, slug):
        from loadwarrior.locust import candidates
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
        assert out == [path('./')/fn, venv/'etc'/fn, path('/etc')/fn ], out


class TestConfigFinder(unittest.TestCase):
    def test_noerror(self):
        from loadwarrior.locust import find_config
        gen = lambda x: [path(x) for x in 'can\'texist.blm', __file__]
        out = find_config(__file__, candidates=gen)
        assert out == __file__

    @tools.raises(ValueError)
    def test_notfound_raise_error(self):
        from loadwarrior.locust import find_config
        gen = lambda x: [path(x) for x in ('can\'texist.blm',)]
        find_config(__file__, candidates=gen)

    def test_notfound_no_raise(self):
        from loadwarrior.locust import find_config
        gen = lambda x: [path(x) for x in ('can\'texist.blm',)]
        assert find_config(__file__, candidates=gen, raise_error=False) is None

