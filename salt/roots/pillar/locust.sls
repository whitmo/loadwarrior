statsd:
  setup: loadwarrior.statsdext.register_statsd_emitters  
  host: monitoring
  port: 8125
  sample_rate: 0.50
loci:
  - smlt.anonweb.Anon