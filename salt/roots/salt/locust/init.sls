locust-pkgs:
  pkg.installed:
    - names:
      - git
      - python-dev
      - libzmq-dev


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


/opt/lw-locust/etc/locust.yml:
  file.managed:
    - source: salt://locust/locustfile.yml
    - makedirs: True
    - mode: 755