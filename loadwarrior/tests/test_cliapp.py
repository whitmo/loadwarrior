import unittest
from path import path
from stuf import stuf

class TestApp(unittest.TestCase):
    here = path(__file__).parent
    gcf = here / "test_config.yml"
    options = stuf(host='localhost',
                   locust_port=123,
                   circus_port=456,
                   target_url='http://the.url')
    
    def makeone(self):
        from loadwarrior.cli import CLIApp
        CLIApp.default_config = self.gcf
        return CLIApp()

    def test_default_config(self):
        app = self.makeone()
        settings = app.gc
        assert self.gcf.exists()
        assert 'target_url' in settings
        assert settings.target_url is None

    def test_locust_make_cmd(self):
        app = self.makeone()
        app.options = self.options
        assert callable(app.make_loci_cmd)
        assert app.make_loci_cmd(role='--slave').endswith('--slave')

    def test_locust_url(self):
        app = self.makeone()
        app.options = self.options
        assert app.locust_url == 'http://localhost:123'

    def test_circus_endpoint(self):
        app = self.makeone()
        app.options = self.options
        assert app.circus_endpoint == 'tcp://localhost:456'
                
    def tearDown(self):
        if self.gcf.exists():
            self.gcf.remove()
