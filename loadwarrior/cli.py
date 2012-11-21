#from . import models
from circus.client import CircusClient
from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager
from functools import partial
from itertools import count
from loadwarrior.utils import reify
from path import path
import sys
from pprint import pformat
from stuf import frozenstuf
from stuf import stuf
import gevent
import hashlib
import json
import logging
import pkg_resources
import re
import requests
import sys
import time
import yaml
import shlex

log = logging.getLogger(__name__)


class CLIApp(App):
    """
    command line interface
    """
    def_slave_num = 10
    log = log
    specifier = 'loadwarrior.cli'
    version = pkg_resources.get_distribution('loadwarrior').version
    default_config = path('~/.loadwarrior/global.yml').expanduser()
    config_template = dict(
        circus_port=5565,
        locust_port=8889,
        host='localhost',
        target_url=None,
        running=False)
    cclient_factory = CircusClient

    def __init__(self):
        self._settings = None
        super(CLIApp, self).__init__(
            description=self.specifier,
            version=self.version,
            command_manager=CommandManager(self.specifier)
        )

    @reify
    def gc(self):
        return frozenstuf(self._load_config(self.default_config))

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(CLIApp, self).build_option_parser(description, version, argparse_kwargs=argparse_kwargs)
        parser.add_argument('--circus-port',
                            type=int,
                            default=self.gc.circus_port,
                            help="circus endpoint")

        parser.add_argument('--locust-port',
                            type=int,
                            default=self.gc.locust_port,
                            help="URL of locust master")

        parser.add_argument('--host',
                            default=self.gc.host,
                            help="IP or domain name of where locust and circus are running")

        tg_kw = dict(help="current target of testing")
        tg =  self.gc.get('target_url', None)
        if tg is not None:
            tg_kw['default'] = tg
        parser.add_argument('--target_url', '-t', **tg_kw)
        return parser

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def _load_config(self, confp):
        lw_folder = confp.parent
        if not lw_folder.exists():
            lw_folder.mkdir()

        if not confp.exists():
            self.write_yml(confp, self.config_template)

        with open(confp) as stream:
            return yaml.load(stream)

    @staticmethod
    def write_yml(fpath, data):
        fpath.write_text(yaml.dump(data, default_flow_style=False))
        return fpath

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

    remote_locust_env = path('/opt/lw-locust')

    # --slave
    cmd_tmplt = '{env}/bin/locust -P {port} -H {target_url} -f {env}/share/locustfile.py {role}'
    role_tmplt = '--{role} {extra}'

    @reify
    def locust_url(self):
        return "http://{0}:{1}".format(self.options.host, self.options.locust_port)

    @reify
    def make_loci_cmd(self):
        return partial(self.cmd_tmplt.format,
                       target_url=self.options.target_url,
                       env=self.remote_locust_env,
                       port=self.options.locust_port)

    @reify
    def circus_endpoint(self):
        return "tcp://{0}:{1}".format(self.options.host, self.options.circus_port)

    @reify
    def urlsig(self):
        return hashlib.sha1(self.options.target_url).hexdigest()[:8]

    slug = 'loadwarrior'

    @property
    def master_and_slave(self):
        for name in '.master', '.slave':
            ret = self.circus_call('stats', name=self.slug + name)
            if ret['status'] == 'error':
                yield None
            else:
                yield ret['info']

    unworking = set(('No such process (stopped?)',))

    @property
    def loci_up(self):
        master, slave = self.master_and_slave
        if not all((master, slave)):
            return False

        opts = self.circus_call('options', name=master)
        url = self.extract_url(opts['options']['cmd']).groupdict('url')

        if url != self.options.target_url.strip():
            self.circus_call('rm', name=slave)
            self.circus_call('rm', name=master)
            return False
        return True

    extract_url = staticmethod(re.compile(".* -H (?P<url>http://.*) -f").match)

    @reify
    def cclient(self):
        #@@ add ssh support??
        self.log.info("Circus client: %s" %self.circus_endpoint)
        return CircusClient(endpoint=self.circus_endpoint)

    @staticmethod
    def ccmd(command, **props):
        return dict(command=command, properties=props)

    def clear_locust(self):
        self.circus_call('rm', name=self.slug + '.master')
        self.circus_call('rm', name=self.slug + '.slave')

    def circus_call(self, command, **props):
        out = self.cclient.call(self.ccmd(command, **props))
        if out['status'] != 'ok':
            self.log.error(out)
        return out

    def prep_loci(self):
        if not self.loci_up:
            #@@ refactor command generation??
            # use circus env to handle
            # - target
            # - locust class
            # -
            master_cmd = self.make_loci_cmd(role=self.role_tmplt.format(role='master', extra=''))
            self.log.info(master_cmd)
            master_cmd = shlex.split(master_cmd)
            basecmd = master_cmd.pop(0)

            slave_cmd = self.make_loci_cmd(role=self.role_tmplt.format(role='slave', extra=''))
            self.log.info(slave_cmd)
            slave_args = shlex.split(slave_cmd)[1:]

            self.log.info(slave_args)
            # fire up new ones
            #@@ make slaves numprocs parameterizable
            master_options = dict(shell=False,
                           max_retry=1,
                           stdout_stream={
                               'class':'FileStream',
                               'filename':'/var/log/loadwarrior.log',
                               'refresh_time':0.3},
                           stderr_stream={
                               'class':'FileStream',
                               'filename':'/var/log/loadwarrior.log',
                               'refresh_time':0.3})

            self.circus_call('add', cmd=basecmd, start=True,
                             name=self.slug + ".master",
                             args=" ".join(master_cmd),
                             options=master_options)

            slave_options = master_options.copy()
            slave_options['numprocesses'] = self.def_slave_num
            self.circus_call('add', cmd=basecmd, start=True,
                             name=self.slug + ".slave",
                             args=" ".join(slave_args),
                             options=slave_options)
            
            self.test_connection(self.locust_url + '/stop')

    def test_connection(self, url, total_time=5, wait=0.5):
        """
        If
        """
        gevent.sleep(wait)
        with gevent.Timeout(8, RuntimeError('%s not up' %self.locust_url)):
            while True:
                try:
                    res = requests.get(url)
                    if res.content:
                        return True
                except requests.ConnectionError:
                    gevent.sleep(wait)


"""
http://monitoring/render/?width=1123
&height=566
&_salt=1351798791.597
&target=stats.timers.lt.response.*.lower
&target=stats.timers.lt.response.*.mean
&target=stats.timers.lt.response.*.mean_90
&target=scale(stats.gauges.lt.count%2C100)
&target=scale(mt1.mt1-pyweb01.nginx.active_connections%2C10)
&target=stats.timers.lt.response.*.upper_90
&target=scale(mt1.mt1-pyweb01.loadavg.05%2C1000)
&target=scale(mt1.mt1-pyweb01.loadavg.01%2C1000)
&graphOnly=false
&hideLegend=false
&title=Loadtest%20metrics
&from=12%3A30_20121101
"""
class Timer(stuf):
    def __init__(self):
        self.start = None
        self.final = None

    @property
    def elapsed(self):
        if self.final is None:
            return time.time() - self.start
        return self.final

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, tb):
        self.final = self.elapsed
        self.end = time.time()
        return False


class Bench(Command):
    """Run a benchmark"""

    log = log
    timer = Timer()

    def get_parser(self, prog_name):
        parser = super(Bench, self).get_parser(prog_name)
        parser.add_argument('--interval', '-i', type=int, default=60*5)
        parser.add_argument('--cohort', '-c', default="10:20:40:60:80:100")
        parser.add_argument('--rate', '-r', default=20)
        parser.add_argument('--sample-interval', '-s', type=int, default=10)
        #parser.add_argument('url', type=str)
        return parser

    def take_action(self, pargs):
        self.app.clear_locust()
        assert self.app.options.target_url, "No target url"
        self.app.prep_loci()
        cohorts = [int(x) for x in pargs.cohort.split(':')]
        with self.timer:
            for group in cohorts:
                out = [data for data in self.runner(self.app.locust_url, group,
                                                    pargs.rate, pargs.interval,
                                                    pargs.sample_interval)]
        self.log.info("&from=%(start)d&until=%(end)d %(final)s" %self.timer)
        return out

    def stats_report(self, url):
        stats = requests.get(url + 'stats/requests').content
        data = json.loads(stats)
        return data

    def runner(self, url, howmany, rate, interval, sample_interval):
        self.log.info("%d start" %howmany)
        ramp = howmany/rate
        total_time = ramp + interval
        if not url.endswith('/'):
            url = url + '/'

        res = requests.get(url + 'stop')
        self.log.info(res.content)
        with gevent.Timeout(total_time, False):
            res = requests.post(url + 'swarm',
                                data=dict(locust_count=howmany,
                                          hatch_rate=rate))
            self.log.info(res.content)
            while True:
                gevent.sleep(sample_interval)
                yield self.stats_report(url)

        res = requests.get(url + 'stop')
        self.log.info("%d end" %howmany)


def main(argv=sys.argv[1:], app=CLIApp):
    return app().run(argv)
