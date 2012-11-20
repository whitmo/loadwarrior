nginx-ppa:
  cmd.run:
    - name: "add-apt-repository -Y ppa:nginx/stable && apt-get update"
    - unless: "[ -f /etc/apt/sources.list.d/nginx-stable-{{ grains['oscodename'] }}.list ]"

nginx:
  pkg:
    - latest
    - require:
      - cmd.run: nginx-ppa  
  service:
    - running
    - watch:
      - file: nginxconf

nginxconf:
  file.managed:
    - name: /etc/nginx/sites-enabled/default
    - source: salt://nginx/nginx.conf
    - template: jinja
    - makedirs: True
    - mode: 755

