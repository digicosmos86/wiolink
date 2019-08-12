# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/xenial64"

  # Provision script to install dependencies used by the esp-open-sdk and
  # micropython tools.  First install dependencies as root.
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    echo "Installing esp-open-sdk, Espressif ESP-IDF, and micropython dependencies..."
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends apt-utils
    sudo apt-get install -y build-essential git make unrar-free unzip \
                            autoconf automake libtool gcc g++ gperf \
                            flex bison texinfo gawk ncurses-dev libexpat-dev \
                            python sed libreadline-dev libffi-dev pkg-config \
                            help2man python-dev python-serial wget bash bzip2 vim libtool-bin \
                            screen sudo curl libtool-bin python3

    sudo echo "vagrant ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
    echo "Installing Espressif ESP32 toolchain..."
    cd /home/vagrant

    git clone --recursive https://github.com/pfalcon/esp-open-sdk.git /home/vagrant/esp-open-sdk
    cd /home/vagrant/esp-open-sdk/
    make
    
    echo "PATH=$(pwd)/xtensa-lx106-elf/bin:\$PATH" >> ~/.profile
    echo "SDK_BASE=/home/vagrant/esp-open-sdk/sdk" >> ~/.profile
    echo "ESP_HOME=/home/esp/esp-open-sdk" >>/.profile
    source ~/.profile

    cd /home/vagrant/wiolink
  SHELL

  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/home/vagrant/wiolink"

  # Virtualbox VM configuration.
  config.vm.provider "virtualbox" do |v|
    # Bump the memory allocated to the VM up to 1 gigabyte as the compilation of
    # the esp-open-sdk tools requires more memory to complete.
    v.memory = 1024
    # Enable USB.
    v.customize ["modifyvm", :id, "--usb", "on"]
  end

end