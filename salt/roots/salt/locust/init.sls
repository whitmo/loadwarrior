locust-pkgs:
  pkg.installed:
    - names:
      - git
      - python-dev
      - zeromq

/opt/lw-locust:
  virtualenv.manage:
    - no_site_packages: True
    - requirements: salt://locust/reqs.txt
      