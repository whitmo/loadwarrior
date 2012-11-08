# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  config.vm.network :hostonly, "192.168.33.10"
  config.ssh.forward_agent = true

  #config.vm.network :bridged
  # config.vm.forward_port 80, 8080
  # config.vm.share_folder "v-data", "/vagrant_data", "../data"

  config.vm.provision :salt do |salt|
    salt.run_highstate = true

    ## Optional Settings:
    salt.minion_config = "salt/minion.conf"
    # salt.salt_install_type = "git"
    # salt.salt_install_args = "develop"

    ## Only Use these with a masterless setup to
    ## load your state tree:
    salt.salt_file_root_path = "salt/roots/salt"
    salt.salt_pillar_root_path = "salt/roots/pillar"

    ## If you have a remote master setup, you can add
    ## your preseeded minion key
    # salt.master = true
    # salt.minion_key = "salt/key/testing.pem"
    # salt.minion_pub = "salt/key/testing.pub"
  end
end




