from nose import tools
from path import path
import unittest


class TestConfigFinder(unittest.TestCase):
    
    def test_noerror(self):
        from loadwarrior.utils import find_config
        gen = lambda x: [path(x) for x in 'can\'texist.blm', __file__]
        out = find_config(__file__, candidates=gen)
        assert out == __file__

    @tools.raises(ValueError)
    def test_notfound_raise_error(self):
        from loadwarrior.utils import find_config
        gen = lambda x: [path(x) for x in ('can\'texist.blm',)]
        find_config(__file__, candidates=gen)

    def test_notfound_no_raise(self):
        from loadwarrior.utils import find_config
        gen = lambda x: [path(x) for x in ('can\'texist.blm',)]
        assert find_config(__file__, candidates=gen, raise_error=False) is None
