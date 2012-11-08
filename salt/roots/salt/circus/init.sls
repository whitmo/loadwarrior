circus-ppa:
  cmd.run:
    - name: "apt-add-repository -Y ppa:roman-imankulov/circus && apt-get update"
    - unless: "[ -f /etc/apt/sources.list.d/roman-imankulov-circus-{{ grains['oscodename'] }}.list ]"

circus-pkgs:
    pkg.installed: 
    - names: 
      - python-chaussette
      - circus
    - require:
      - cmd.run: circus-ppa

circus:
  service.running:
    - require:
      - pkg: circus
      - file: /etc/circus/circusd.ini
    - names:
        - circus
    - watch:
        - file: /etc/circus/circusd.ini

/etc/circus/circusd.ini:
  file.managed:
    - source: salt://circus/circusd.ini



