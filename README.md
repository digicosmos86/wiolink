# The GrowThings library

This repository contains source code and all other files required to build a custom firmware with the GrowThings package for the WioLink development board. For instruction on how to flash the firmware and how to use the library, please refer to [The GrowThings Documentation](http://growthings.readthedocs.io).

We recommend that you follow the instruction below to [build the firmware with Docker](#Getting-Started-with-Docker). Some operating systems do not support Docker (e.g. Windows 10 Home). If that is the case, then please follow the [Getting Started with Vagrant](#Getting-Started-with-Vagrant) section to build the firmware in a virtual machine (VM).

## Getting Started with Docker

The following instruction will guide you through the necessary steps to build the binary file of the firmware within a Docker container. You can then flash the firmware to the board.

### Step 1. Install Docker

We will use Docker for the firmware building process. Please follow the links below for instructions on how to install Docker Community Edition (CE) on your computer's operating system

* [Installing Docker on Windows](https://docs.docker.com/docker-for-windows/install/)
* [Installing Docker on MacOS](https://docs.docker.com/docker-for-mac/install/)
* [Installing Docker on Linux](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

### Step 2. Clone this repo

Git is required for this process. Please make sure you have git installed on your computer, then in your system terminal type:

``` bash
git clone https://github.com/digicosmos86/wiolink
cd wiolink
```

### Step 3. Build the Docker image from the Dockerfile

The Dockerfile in this repo contains all instructions needed for Docker to build the image for the container that contains the toolchain that we need to build the firmware. In your command line, enter the following command:

``` bash
docker build -t espbuild .
```

Do not forget the period `.` at the end of the line. This process might take a while.

### Step 4. Launch the Docker container for the first time

Now we can run the Docker container from the built image. The key step of this is to make sure that the current folder is bound to the `~/wiolink` folder of the container. To do so, on a Windows machine, you need to go to `Docker Settings` > `Shared Drives`, and check the drive on which the cloned repo is located. After this step, run the following command:

``` bash
docker run -it -v $SOURCE:/home/esp/wiolink espbuild zsh
```

Substitute `$SOURCE` with the absolute path of the cloned repo. This will launch the container and give the user terminal access to it.

### Step 5. Build the firmware

The two shell script will handle all the procedures needed to build the firmware. When logged into the container for the first time, run the `init.sh` file.

``` bash
bash init.sh
```

Then there is no need to run this file again. Just run `build.sh` whenever any changes are made to the source code.

``` bash
bash build.sh
```

This will recompile the firmware. Once complete, the latest version of the firmware can be found under the `build` folder of the repository.

### Step 6. Reuse the container and rebuild the firmware

To check if the container is still active, use `docker ps`. If the container is still up and running, the container based on image `espbuild` will be listed. You can the name or ID of the container from the list. Use either the name or ID to substitute `$ID` below to get back into the container:

``` bash
docker exec -it $ID zsh
```

If the container based on image `espbuild` is not shown in the list, the container is stopped. Use `docker ps -a` to find out the name or the ID of the container. Then, use the following command to get back into the container:

``` bash
docker start -i $ID
```

## Getting Started with Vagrant

The following instruction will guide you through the necessary steps to build the binary file of the firmware within a Virtual Machine. You can then flash the firmware to the board.

### Step 1. Install Vagrant and Virtual Box

Please follow the links below to install VirtualBox and Vagrant. After installing Vagrant, you might be prompted to restart your computer.

* [Installing VirtualBox](https://www.virtualbox.org/)
* [Installing Vagrant](https://www.vagrantup.com/downloads.html)

### Step 2. Clone this repo

Git is required for this process. Please make sure you have git installed on your computer, then in your system terminal type:

``` bash
git clone https://github.com/digicosmos86/wiolink
cd wiolink
```

### Step 3. Provision the VM with Vagrant

Use the following command to provision the VM:

``` bash
vagrant up
```

Vagrant will automatically use the information in the `Vagrantfile` to provision the VM and build the toolchain for compiling the firmware. This is a fairly long process that should take around 30 minutes.

### Step 4. SSH into the VM

After the VM has been provisioned, use the following commands to SSH into the VM:

``` bash
vagrant ssh
cd ~/wiolink
```

Please remember the second line of the command to set the current working directory to `~/wiolink`.

### Step 5. Build the firmware

The two shell script will handle all the procedures needed to build the firmware. When logged into the container for the first time, run the `init.sh` file.

``` bash
bash init.sh
```

Then there is no need to run this file again. Just run `build.sh` whenever any changes are made to the source code.

``` bash
bash build.sh
```

This will recompile the firmware. Once complete, the latest version of the firmware can be found under the `build` folder of the repository.

### Step 6. Shutting down and/or Destroy the VM

After building the firmware, type `exit` to exit `ssh`.

The VM will still be up and running. Use `vagrant halt` to shutdown the VM and `vagrant up` to start it again. If there is absolutely no need for the VM, you can use `vagrant destroy` to permanently delete the VM.