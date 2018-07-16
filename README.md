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

## Directory Overview
* /atm/ - Code for card provisioning and ATM operation which runs on the Beagle Bone Black (BBB)
* /atm/interface/ - Interface code for the BBB to communicate with the card and bank
* /bank/ - Code for the bank which runs on the laptop
* /CARD.cydsn/ - Code for the ATM card which runs on the PSoC
* /Build_Program.py - Compiles and programs an ATM card (PSoC)

## Installing Dependencies

### PSoC Creator 4.2 (Requires Windows System)
* Download installer from http://www.cypress.com/products/psoc-creator-integrated-design-environment-ide
* Run installer and follow steps

## Setup
* Connect BBB to laptop by miniUSB port
* Run `scp ./atm/ <BBB IP>:~` to copy ATM files to BBB
* Connect serial debug of BBB to laptop via Bus Pirate
* Launch PuTTY or other serial terminal and connect to Bus Pirate
* Configure Bus Pirate to UART (commands: `m, 3, 9, 1, 1, 1, 2, (3)`)
* Login with default user/password
* Attach PSoC to USB port of BBB
* Attach 5-pin programmer to PSoC and run `Build_Program.py`
* When complete, on the laptop, run `python ./bank/provision_update.py [port]`
* On the BBB, run `python ~/atm/provision_tool.py [balance] [c_port] [b_port]`
  where `[balance]` is the starting balance `[c_port]` is the port from
  the BBB to the ATM card, and `[b_port]` is the port from the BBB to the bank
* After card is provisioned, run `python ~/atm/atm.py` to start ATM
* Run `python ./bank/bank.py [port]` where `[port]` is the valid serial port
* System is now ready for use
