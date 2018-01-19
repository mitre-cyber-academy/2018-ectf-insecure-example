# Collegiate eCTF 2018

## Bank Server

The interface wrapped in REQUIRED INTERFACE must be supported by your implementation. The interface wrapped in DEVELOPMENT INTERFACE was used during the development and testing of the reference implementation. It is recommended that team's extend or implement their own development interface for testing.

### -------*BEGIN : REQUIRED INTERFACE*--------


### Build and Run Bank Server (Docker)

#### Build the bank_server image:

* *If no image exists, build image.*
* *If image exists, rebuild image.*

    (cd bank_server && make build)

#### Start the bank_server container:

* *If no container is running or stopped, create and start container.*
* *If container is stopped, start container*
* *If container is running, do nothing.*

    (cd bank_server && make start)

##### *note: your system must be persistent across start and stop.*

#### Stop the bank_server container:

* *If container is running, stop container*
* *If container is stopped, do nothing.*

    (cd bank_server && make stop)

#### Stop the bank_server container and remove the bank_server image:

* *If container is running, stop and remove container*
* *If container is stopped, remove container*
* *If container is does exist, do nothing*

    (cd bank_server && make clean)

#### Save logs from the bank_server container:

* *If container is running, output logs*
* *If container is stopped, do nothing*
* *If container is does exist, do nothing*

    (cd bank_server && make logs) // saved to /logs/*

### -------*END : REQUIRED INTERFACE*--------

### -------*BEGIN : DEVELOPMENT INTERFACE*--------

#### Test functionality of AdminInterface (Standard) and ATM-BankInterface (Specific to Reference Implementation):

    (cd bank_server && make test)

### -------*END : DEVELOPMENT INTERFACE*--------
