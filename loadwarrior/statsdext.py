from functools import partial
from locust import events
from statsd.timer import Timer as BaseTimer
from stuf import stuf
import statsd


class Timer(BaseTimer):

    def send_raw(self, subname, ms):
        '''Send the data to statsd via self.connection

        :keyword subname: The subname to report the data to (appended to the
            client name)
        :keyword ms: milleseconds to report
        '''
        name = self._get_name(self.name, subname)
        self.logger.info('%s: %dms', name, ms)
        return self._send({name: '%d|ms' % ms})


class LoadStats(stuf):
    default_prefix = 'lw'

    def __init__(self, **kw):
        stuf.__init__(self, **kw)
        self.prefix = self.get('prefix', self.default_prefix)
        self.statsd_cxn = statsd.Connection(self.host, self.port, self.sample_rate)
        self.rescount = statsd.Counter(self.prefix, self.statsd_cxn)
        self.response_timer = Timer(self.prefix, self.statsd_cxn)
        self.loci_error = statsd.Counter(self.prefix, self.statsd_cxn)
        self.users_g = statsd.Gauge(self.prefix, self.statsd_cxn)

    def report_request(self, method, path, res_time, response, slug=''):
        self.rescount.increment(slug)
        if response is not None:
            self.rescount.increment(slug + ".%s" %response.code)
        self.response_timer.send_raw(slug, res_time)

    def report_failure(self, method, path, res_time, exc, response):
        slug = "failure"
        self.report_request(method, path, res_time, response, slug)

    def locust_error(self, loc, exc, tb):
        self.loci_error.increment("error.%s" %exc)

    def users(self, user_count):
        self.users_g.send("count", user_count)


def register_statsd_emitters(port, host, sample_rate=0.5, loader=LoadStats, hooks=events):
    """
    Hook up our statsd reporting
    """
    stats = loader(port=port,
                      host=host,
                      sample_rate=sample_rate)

    hooks.request_success += partial(stats.report_request, slug="success")
    hooks.request_failure += stats.report_failure
    hooks.locust_error += stats.locust_error
    hooks.quitting += partial(stats.users, 0)
    hooks.hatch_complete += stats.users
    return stats

