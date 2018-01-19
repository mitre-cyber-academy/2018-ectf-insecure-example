# Collegiate eCTF 2018

## ATM Backend

The interface wrapped in REQUIRED INTERFACE must be supported by your implementation. The interface wrapped in DEVELOPMENT INTERFACE was used during the development and testing of the reference implementation. It is recommended that team's extend or implement their own development interface for testing.

### -------*BEGIN : REQUIRED INTERFACE*--------


### Build and Run atm_backend (Docker)

#### Build the atm_backend image:

* *If no image exists, build image.*
* *If image exists, rebuild image.*

    (cd atm_backend && make build)

#### Start the atm_backend container:

* *If no container is running or stopped, create and start container.*
* *If container is stopped, start container*
* *If container is running, do nothing.*

    (cd bank_server && make start)

##### *note: your system must be persistent across start and stop.*

#### Stop the atm_backend container:

* *If container is running, stop container*
* *If container is stopped, do nothing.*

    (cd atm_backend && make stop)

#### Stop the atm_backend container and remove the atm_backend image:

* *If container is running, stop and remove container*
* *If container is stopped, remove container*
* *If container is does exist, do nothing*

    (cd atm_backend && make clean)

#### Save logs from the atm_backend container:

* *If container is running, output logs*
* *If container is stopped, do nothing*
* *If container is does exist, do nothing*

    (cd atm_backend && make logs) // saved to /logs/*

### -------*END : REQUIRED INTERFACE*--------

### -------*BEGIN : DEVELOPMENT INTERFACE*--------

#### Test functionality of ATMInterface (Standard) and ProvisionInterface (Standard):

    (cd atm_backend && make test)

### -------*END : DEVELOPMENT INTERFACE*--------
