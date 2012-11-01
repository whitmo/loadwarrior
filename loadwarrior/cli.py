from cliff.app import App
from cliff.command import Command
from cliff.commandmanager import CommandManager
import gevent
import logging
import pkg_resources
import sys
import requests
import json
import time
from stuf import stuf

log = logging.getLogger(__name__)


class CLIApp(App):
    """
    command line interface 
    """
    log = log
    specifier = 'loadwarrior.cli'
    version = pkg_resources.get_distribution('loadwarrior').version
    
    def __init__(self):
        super(CLIApp, self).__init__(
            description=self.specifier,
            version=self.version,
            command_manager=CommandManager(self.specifier),
            )
    
    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

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
    "Does a bench run"

    log = log

    def get_parser(self, prog_name):
        parser = super(Bench, self).get_parser(prog_name)
        parser.add_argument('--interval', '-i', type=int, default=60*5)
        parser.add_argument('--cohort', '-c', default="10:20:40:60:80:100")
        parser.add_argument('--rate', '-r', default=20)
        parser.add_argument('--sample-interval', '-s', type=int, default=10)
        parser.add_argument('url', type=str)
        return parser

    def take_action(self, pargs):
        cohorts = [int(x) for x in pargs.cohort.split(':')]
        timer = Timer() 
        with timer:
            for group in cohorts:
                out = [data for data in self.runner(pargs.url, group,
                                                    pargs.rate, pargs.interval,
                                                    pargs.sample_interval)]
        self.log.info("&from=%(start)d&until=%(end)d %(final)s" %timer)
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
            res = requests.post(url + 'swarm', data=dict(locust_count=howmany, hatch_rate=rate))
            self.log.info(res.content)
            while True:
                gevent.sleep(sample_interval)
                yield self.stats_report(url)
        res = requests.get(url + 'stop')
        self.log.info("%d end" %howmany)



class TestEnds(Exception):
    """
    The test has ended
    """




def main(argv=sys.argv[1:], app=CLIApp):
    return app().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))    
    
