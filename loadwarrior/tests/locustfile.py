from loadwarrior.locustext import setup
from path import path
setup(__name__, conffile=path(__file__).parent/'test_locust.yml')
