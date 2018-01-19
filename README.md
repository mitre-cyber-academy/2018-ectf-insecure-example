# Embedded CTF Example Code

This repository contains an example reference system for MITRE's 2018 
[Embedded System CTF](http://mitrecyberacademy.org/competitions/embedded/).
This example meets all the requirements outlined in the challenge writeup
document, but is not implemented securely.  

## Disclaimer
This code is incomplete, insecure, and does not meet MITRE standards for
quality.  This code is being provided for educational purposes to serve as a
simple example that meets the minimum functional requirements for the 2018 MITRE
eCTF competition.  Use this code at your own risk!

# Getting started

## Installing Dependencies

### Recommended Docker environment on Windows 10 (Required for Home edition) and MacOS:

* Download and install Docker Toolbox:
    - https://docs.docker.com/toolbox/overview/
    - If system already has VirtualBox installed, uncheck box
    - If system already has Git installed, uncheck box

### Recommended Docker environment on Linux:

* Download and install "native" Docker
* Install VirtualBox to run Windows VM for PSoC Creator and Programmer software

### Alternative Docker environment on Windows 10 Pro and MacOS:
* Download and install VirtualBox
* Download and install Docker
    - When Docker launches it will tell you to enable Hyper-V, which in turn will disable VirtualBox.  
    - Do NOT enable Hyper-V
    - Note: by not enabling Hyper-V normal Docker usage will not work.  It will only work through Docker Machine

### Windows Environment Setup (Suggested):
* Download and install Cygwin
    - Search for ‘socat’ and ‘GNU make’ during installation
    - Click ‘Skip’ on these packages to show the version that will be installed
* Add Cygwin executables to the system PATH
    - Open ‘System Properties:Advanced’ and click ‘Evironment Variables’
    - Add Cygwin’s installation directory (typically ‘C:\cygwin64\bin’) to the front of the ‘Path’ system variable
    - Now all of the Cygwin Unix functions are available in all terminals
* Download and install Python
* (The following instructions assume that ‘make’, ‘socat’, and ‘python’ are available on the Path)

### Initializing Docker-Machine on all platforms:
* Open a terminal (‘Docker Quickstart Terminal’ for Windows or Mac)
* (If using Docker-Machine) Build a Docker container VM
     - Create a docker machine: `docker-machine create --driver virtualbox default`
     - Check that VM was created successfully: `docker-machine ls`
     - Find the IP address of the VM: `docker-machine ip`
     - If you ever need to administer the VM, you can ssh into the machine: `docker-machine ssh`
     - Enable USB in VirtualBox
          * Stop VM: `docker-machine stop default`
          * Use VirtualBox settings to enable USB
          * Start VM: `docker-machine start default`
* Build reference containers and start servers
     - Move into bank server directory: `cd bank_server`
     - Start the bank server and container: `make start`
	 - Move into ATM backend directory: `cd ../atm_backend`
     - Start the ATM backend server and container: `make start`

* Allow local interface code to connect to the servers running on the VM (requires redirection of network traffic)
     - `socat TCP-LISTEN:1336,fork,reuseaddr TCP:<IP address of VM>:1336 &`
     - `socat TCP-LISTEN:1338,fork,reuseaddr TCP:<IP address of VM>:1338 &`
* Verify connectivity to servers
     - Move to interface directory: `cd ../interfaces`
     - Start admin interface: `python admin_interface.py`
          * Type `create_atm testatm.info`
          * If successful, a long string of random characters will be returned and outputed to a file named testatm.info
          * Type `create_account testaccount 120 testaccount.info`
          * If successful, a long string of random characters will be returned and outputed to a file named testaccount.info
          * Type `exit`
     - Start provision interface: `python provision_interface.py`
          * Type `provision\_atm testatm.info test\_billfile`
          * If successful, True will be returned
          * Type `provision\_card testaccount.info '12345678'`
          * If successful, True will be returned
     - Start atm interface: ‘python atm_interface.py’
          * Type `check_balance '12345678'`
          * If successful, 120 will be returned
          * Type `withdraw'12345678' 10`
          * If successful, 10 bills will be returned
          * Type `change_pin '12345678' '87654321'`
          * If successful, True will be returned

### Install PSoC Creator 4.1 (Requires Windows System)
* Download installer from http://www.cypress.com/products/psoc-creator-integrated-design-environment-ide
* Run installer and follow steps

### Use PSoC Creator 4.1 to program security_module
* Open ectf-workspace.cywrk
* Right-click the security_module project in the left pane and select set active project
* Plug-in MiniProg and PSoC
* Connect MiniProg to PSoC using 5-pin adapter
* Select Debug and Program

## Building and Running

The following interface is supported by the reference implementation and MUST
be supported by your implementation. The following commands apply to both the
atm\_backend and the bank\_server.

### Build the component image:

* *If no image exists, build image.*
* *If image exists, rebuild image.*
     - `(cd bank_server && make build)`
     - `(cd atm_backend && make build)`

### Start the component container:

* *If no container is running or stopped, create and start container.*
* *If container is stopped, start container*
* *If container is running, do nothing.*
     - `(cd bank_server && make start)`
     - `(cd atm_backend && make start)`

#### *note: your system must be persistent across start and stop.*

### Stop the component container:

* *If container is running, stop container*
* *If container is stopped, do nothing.*
     - `(cd bank_server && make stop)`
     - `(cd atm_backend && make stop)`

### Stop the component container and remove the component image:

* *If container is running, stop and remove container*
* *If container is stopped, remove container*
* *If container is does exist, do nothing*
     - `(cd bank_server && make clean)`
     - `(cd atm_backend && make clean)`

### Save logs from the component container:

* *If container is running, output logs*
* *If container is stopped, do nothing*
* *If container is does exist, do nothing*
     - `(cd bank_server && make logs)` // saved to /logs/*
     - `(cd atm_backend && make logs)` // saved to /logs/*

## Other Examples

### Example 'socat' commmand to redirect TCP traffic
`socat TCP-LISTEN:1336,fork,reuseaddr TCP:192.168.99.100:1336 &`
`socat TCP-LISTEN:1338,fork,reuseaddr TCP:192.168.99.100:1338 &`


