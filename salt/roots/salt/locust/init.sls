locust-pkgs:
  pkg.installed:
    - names:
      - git
      - python-dev
      - libzmq-dev
      - swig


venv:
  virtualenv.manage:
    - name: /opt/lw-locust
    - distribute: True
    - no_site_packages: True


locust-code:
  pip.installed:
    - name: ''
    - download-cache: /opt/.pypkg 
    - bin_env: /opt/lw-locust 
    - requirements: salt://locust/reqs.txt
    - require:
        - virtualenv: venv
        - pkg: locust-pkgs

/etc/loadwarrior/locust.yml:
  file.managed:
    - source: salt://locust/locust.yml
    - makedirs: True
    - mode: 655


/opt/lw-locust/share/locustfile.py:
  file.managed:
    - source: salt://locust/locustfile.py
    - makedirs: True
    - mode: 655