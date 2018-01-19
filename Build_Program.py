#!/usr/bin/env python
# -*- coding: utf-8 -*-

# THIS FILE SHOULD NOT BE CHANGED!

#*******************************************************************************
#* © 2011-2017, Cypress Semiconductor Corporation 
#* or a subsidiary of Cypress Semiconductor Corporation. All rights
#* reserved.
#* 
#* This software, including source code, documentation and related
#* materials (“Software”), is owned by Cypress Semiconductor
#* Corporation or one of its subsidiaries (“Cypress”) and is protected by
#* and subject to worldwide patent protection (United States and foreign),
#* United States copyright laws and international treaty provisions.
#* Therefore, you may use this Software only as provided in the license
#* agreement accompanying the software package from which you
#* obtained this Software (“EULA”).
#* 
#* If no EULA applies, Cypress hereby grants you a personal, non-
#* exclusive, non-transferable license to copy, modify, and compile the
#* Software source code solely for use in connection with Cypress’s
#* integrated circuit products. Any reproduction, modification, translation,
#* compilation, or representation of this Software except as specified
#* above is prohibited without the express written permission of Cypress.
#* 
#* Disclaimer: THIS SOFTWARE IS PROVIDED AS-IS, WITH NO
#* WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING,
#* BUT NOT LIMITED TO, NONINFRINGEMENT, IMPLIED
#* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#* PARTICULAR PURPOSE. Cypress reserves the right to make
#* changes to the Software without notice. Cypress does not assume any
#* liability arising out of the application or use of the Software or any
#* product or circuit described in the Software. Cypress does not
#* authorize its products for use in any products where a malfunction or
#* failure of the Cypress product may reasonably be expected to result in
#* significant property damage, injury or death (“High Risk Product”). By
#* including Cypress’s product in a High Risk Product, the manufacturer
#* of such system or application assumes all risk of such use and in doing
#* so agrees to indemnify Cypress against all liability.
#********************************************************************************
import win32com.client
import os
import array
import subprocess
import threading
import argparse

class enumeCanPowerDevice:
    CAN_MEASURE_POWER = 0x4  # from enum enumCanPowerDevice
    CAN_POWER_DEVICE = 0x1  # from enum enumCanPowerDevice
    CAN_READ_POWER = 0x2  # from enum enumCanPowerDevice
    CAN_MEASURE_POWER_2 = 0x8  # from enum enumCanPowerDevice


class enumCanProgram:
    CAN_PROGRAM_CARBON = 0x1  # from enum enumCanProgram
    CAN_PROGRAM_ENCORE = 0x2  # from enum enumCanProgram


class enumInterfaces:
    I2C = 0x4  # from enum enumInterfaces
    ISSP = 0x2  # from enum enumInterfaces
    JTAG = 0x1  # from enum enumInterfaces
    SWD = 0x8  # from enum enumInterfaces
    SPI = 0x16  # from enum enumInterfaces


class enumFrequencies:
    FREQ_01_5 = 0xc0  # from enum enumFrequencies
    FREQ_01_6 = 0x98  # from enum enumFrequencies
    FREQ_03_0 = 0xe0  # from enum enumFrequencies
    FREQ_03_2 = 0x18  # from enum enumFrequencies
    FREQ_06_0 = 0x60  # from enum enumFrequencies
    FREQ_08_0 = 0x90  # from enum enumFrequencies
    FREQ_12_0 = 0x84  # from enum enumFrequencies
    FREQ_16_0 = 0x10  # from enum enumFrequencies
    FREQ_24_0 = 0x4  # from enum enumFrequencies
    FREQ_48_0 = 0x0  # from enum enumFrequencies
    FREQ_RESET = 0xfc  # from enum enumFrequencies


class enumI2Cspeed:
    CLK_100K = 0x1  # from enum enumI2Cspeed
    CLK_400K = 0x2  # from enum enumI2Cspeed
    CLK_50K = 0x4  # from enum enumI2Cspeed


class enumSonosArrays:
    ARRAY_ALL = 0x1f  # from enum __MIDL___MIDL_itf_PSoCProgrammerCOM_0000_0001
    ARRAY_EEPROM = 0x2  # from enum __MIDL___MIDL_itf_PSoCProgrammerCOM_0000_0001
    ARRAY_FLASH = 0x1  # from enum __MIDL___MIDL_itf_PSoCProgrammerCOM_0000_0001
    ARRAY_NVL_FACTORY = 0x8  # from enum __MIDL___MIDL_itf_PSoCProgrammerCOM_0000_0001
    ARRAY_NVL_USER = 0x4  # from enum __MIDL___MIDL_itf_PSoCProgrammerCOM_0000_0001
    ARRAY_NVL_WO_LATCHES = 0x10  # from enum __MIDL___MIDL_itf_PSoCProgrammerCOM_0000_0001


class enumUpgradeFirmware:
    FINALIZE = 0x3  # from enum enumUpgradeFirmware
    INITIALIZE = 0x0  # from enum enumUpgradeFirmware
    UPGRADE_BLOCK = 0x1  # from enum enumUpgradeFirmware
    VERIFY_BLOCK = 0x2  # from enum enumUpgradeFirmware


class enumValidAcquireModes:
    CAN_POWER_CYCLE_ACQUIRE = 0x2  # from enum enumValidAcquireModes
    CAN_POWER_DETECT_ACQUIRE = 0x4  # from enum enumValidAcquireModes
    CAN_RESET_ACQUIRE = 0x1  # from enum enumValidAcquireModes


class enumVoltages:
    VOLT_18V = 0x8  # from enum enumVoltages
    VOLT_25V = 0x4  # from enum enumVoltages
    VOLT_33V = 0x2  # from enum enumVoltages
    VOLT_50V = 0x1  # from enum enumVoltages
#Define global variables
m_sLastError = ""

#Error constants
S_OK = 0
E_FAIL = -1

#Chip Level Protection constants
CHIP_PROT_VIRGIN = 0x00
CHIP_PROT_OPEN = 0x01
CHIP_PROT_PROTECTED = 0x02
CHIP_PROT_KILL = 0x04
CHIP_PROT_MASK = 0x0F

def SUCCEEDED(hr):
    return hr >= 0

def OpenPort():
    global m_sLastError
    # Open Port - get last (connected) port in the ports list
    hResult = pp.GetPorts()
    hr = hResult[0]
    portArray = hResult[1]
    m_sLastError = hResult[2]    
    if (not SUCCEEDED(hr)): return hr
    if (len(portArray) <= 0):
        m_sLastError = "Connect any Programmer to PC"
        return -1
    bFound = 0
    for i in range(0, len(portArray)):
        if (portArray[i].startswith("MiniProg3") or portArray[i].startswith("TrueTouchBridge") or portArray[i].startswith("KitProg")):
            portName = portArray[i]            
            bFound = 1
            break
    if(bFound == 0):
        m_sLastError = "Connect any MiniProg3/TrueTouchBridge/KitProg device to the PC"
        return -1

    #Port should be opened just once to connect Programmer device (MiniProg1/3,etc).
    #After that you can use Chip-/Programmer- specific APIs as long as you need.
    #No need to repoen port when you need to acquire chip 2nd time, just call Acquire() again.
    #This is true for all other APIs which get available once port is opened.
    #You have to call OpenPort() again if port was closed by ClosePort() method, or
    #when there is a need to connect to other programmer, or
    #if programmer was physically reconnected to USB-port.
            
    hr = pp.OpenPort(portName)
    m_sLastError = hr[1]
    return hr[0]

def ClosePort():    
    hResult = pp.ClosePort()
    hr = hResult[0]
    strError = hResult[1]
    return hr

def OpenPort2():
    global m_sLastError
    # Open Port - get last (connected) port in the ports list
    hResult = pp.GetPorts()
    hr = hResult[0]
    portArray = hResult[1]
    m_sLastError = hResult[2]    
    if (not SUCCEEDED(hr)): return hr
    if (len(portArray) <= 0):
        m_sLastError = "Connect any Programmer to PC"
        return -1
    bFound = 0
    for i in range(0, len(portArray)):
        if (portArray[i].startswith("MiniProg3") or portArray[i].startswith("TrueTouchBridge") or portArray[i].startswith("KitProg")):
            portName = portArray[i]            
            bFound = 1
    if(bFound == 0):
        m_sLastError = "Connect any MiniProg3/TrueTouchBridge/KitProg device to the PC"
        return -1

    #Port should be opened just once to connect Programmer device (MiniProg1/3,etc).
    #After that you can use Chip-/Programmer- specific APIs as long as you need.
    #No need to repoen port when you need to acquire chip 2nd time, just call Acquire() again.
    #This is true for all other APIs which get available once port is opened.
    #You have to call OpenPort() again if port was closed by ClosePort() method, or
    #when there is a need to connect to other programmer, or
    #if programmer was physically reconnected to USB-port.
            
    hr = pp.OpenPort(portName)
    m_sLastError = hr[1]
    return hr[0]

def InitializePort():
    global m_sLastError

    #Setup Power On
    pp.SetPowerVoltage("3.3")
    hResult = pp.PowerOn()
    hr = hResult[0]
    m_sLastError = hResult[1]
    if (not SUCCEEDED(hr)): return hr

    #Set protocol, connector and frequency
    hResult = pp.SetProtocol(enumInterfaces.SWD)
    hr = hResult[0]
    m_sLastError = hResult[1]
    if (not SUCCEEDED(hr)): return hr

    pp.SetProtocolConnector(0) #5-pin connector
    pp.SetProtocolClock(enumFrequencies.FREQ_03_0) #3.0 MHz clock on SWD bus
    
    return hr

def CheckHexAndDeviceCompatibility():
    global m_sLastError
    listResult = []
    result = 0
    hResult = pp.PSoC4_GetSiliconID()
    hr = hResult[0]
    chipJtagID = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)):
        listResult.append(hr)
        listResult.append(result)
        return listResult
    hResult = pp.HEX_ReadJtagID()
    hr = hResult[0]
    hexJtagID = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)):
        listResult.append(hr)
        listResult.append(result)
        return listResult
    result = 1
    for i in range(0, 4):
        if (i == 2): continue #ignore revision, 11(AA),12(AB),13(AC), etc
        if(ord(hexJtagID[i]) != ord(chipJtagID[i])):
            result = 0
            break
    listResult.append(0)
    listResult.append(result)
    return listResult

def PSoC4_IsChipNotProtected():
    global m_sLastError

    #Chip Level Protection reliably can be read by below API (available in VIRGIN, OPEN, PROTECTED modes)
    #This API uses SROM call - to read current status of CPUSS_PROTECTION register (privileged)
    #This register contains current protection mode loaded from SFLASH during boot-up.
    
    hResult = pp.PSoC4_ReadProtection()
    hr = hResult[0]
    flashProt = hResult[1]
    chipProt = hResult[2]
    m_sLastError = hResult[3]
    if (not SUCCEEDED(hr)): return E_FAIL #consider chip as protected if any communication failure
    
    if ((ord(chipProt[0]) & CHIP_PROT_PROTECTED) == CHIP_PROT_PROTECTED):
        m_sLastError = "Chip is in PROTECTED mode. Any access to Flash is suppressed."        
        return E_FAIL

    return S_OK
    
def PSoC4_EraseAll():
    global m_sLastError

    #Check chip level protection here. If PROTECTED then move to OPEN by PSoC4_WriteProtection() API.
    #Otherwise use PSoC4_EraseAll() - in OPEN/VIRGIN modes.

    hr = PSoC4_IsChipNotProtected()    
    if (SUCCEEDED(hr)): #OPEN mode
        #Erase All - Flash and Protection bits. Still be in OPEN mode.
        hResult = pp.PSoC4_EraseAll()
        hr = hResult[0]
        m_sLastError = hResult[1]        
    else:
        #Move to OPEN from PROTECTED. It automatically erases Flash and its Protection bits.
        flashProt = [] #do not care in PROTECTED mode
        chipProt = []
        for i in range(0, 1):
            chipProt.append(CHIP_PROT_OPEN)
        data1 = array.array('B',flashProt) #do not care in PROTECTED mode
        data2 = array.array('B',chipProt)  #move to OPEN

        hResult = pp.PSoC4_WriteProtection(buffer(data1), buffer(data2))
        hr = hResult[0]
        m_sLastError  = hResult[1]        
        if (not SUCCEEDED(hr)): return hr

        #Need to reacquire chip here to boot in OPEN mode.
        #ChipLevelProtection is applied only after Reset.
        hResult = pp.DAP_Acquire()
        hr = hResult[0]
        m_sLastError  = hResult[1]
    return hr

def PSoC4_GetTotalFlashRowsCount(flashSize):
    global m_sLastError
    
    hResult = pp.PSoC4_GetFlashInfo()
    hr = hResult[0]
    rowsPerArray = hResult[1]
    rowSize = hResult[2]
    m_sLastError = hResult[3]
    if (not SUCCEEDED(hr)): return hr

    totalRows = flashSize / rowSize

    return (hr,totalRows,rowSize)

def ProgramFlash(flashSize):
    global m_sLastError
    
    hResult = PSoC4_GetTotalFlashRowsCount(flashSize)
    hr = hResult[0]
    totalRows = hResult[1]
    rowSize = hResult[2]
    if (not SUCCEEDED(hr)): return hr    
    #Program Flash array
    for i in range(0, totalRows):
        hResult = pp.PSoC4_ProgramRowFromHex(i)
        hr = hResult[0]
        m_sLastError = hResult[1]
        if (not SUCCEEDED(hr)): return hr
    return hr    

def PSoC4_VerifyFlash(flashSize):
    global m_sLastError
    
    hResult = PSoC4_GetTotalFlashRowsCount(flashSize)
    hr = hResult[0]
    totalRows = hResult[1]
    rowSize = hResult[2]
    if (not SUCCEEDED(hr)): return hr    
    #Verify Flash array
    for i in range(0, totalRows):        
        hResult = pp.PSoC4_VerifyRowFromHex(i)
        hr = hResult[0]
        verResult = hResult[1]
        m_sLastError = hResult[2]
        if (not SUCCEEDED(hr)): return hr
        if (verResult == 0):
            m_sLastError = "Verification failed on %d row." % (i)
            return E_FAIL
    return hr

def ProgramHSM():
    global m_sLastError
    # Open Port - get last (connected) port in the ports list
    hr = InitializePort()
    if (not SUCCEEDED(hr)): return hr
    
    # Set Hex File ##NEW CODE
    hResult = pp.HEX_ReadFile(os.getcwd() + "\SECURITY_MODULE.cydsn\CortexM0\ARM_GCC_541\Release\SECURITY_MODULE.hex")
    hr = hResult[0]    
    hexImageSize = int(hResult[1])
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    
    #Read chip level protection from hex and check Chip Level Protection mode
    #If it is VIRGIN then don't allow Programming, since it can destroy chip
    hResult = pp.HEX_ReadChipProtection()
    hr = hResult[0]
    hex_chipProt = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    if (ord(hex_chipProt[0]) == CHIP_PROT_VIRGIN):
        m_sLastError = "Transition to VIRGIN is not allowed. It will destroy the chip. Please contact Cypress if you need this specifically."
        return E_FAIL

    # Set Acquire Mode
    pp.SetAcquireMode("Reset")

    #Acquire Device
    hResult = pp.DAP_Acquire()
    hr = hResult[0]
    m_sLastError = hResult[1]
    if (not SUCCEEDED(hr)): return hr
    
    #Check Hex File and Device compatibility
    fCompatibility = 0
    hResult = CheckHexAndDeviceCompatibility()
    hr = hResult[0]
    fCompatibility = hResult[1]    
    if (not SUCCEEDED(hr)): return hr
    if (fCompatibility == 0):
        m_sLastError = "The Hex file does not match the acquired device, please connect the appropriate device"
        return E_FAIL
    
    #Erase All
    hr = PSoC4_EraseAll()
    if (not SUCCEEDED(hr)): return hr

    #Find checksum of Privileged Flash. Will be used in calculation of User CheckSum later    
    hResult = pp.PSoC4_CheckSum(0x8000) #CheckSum All Flash ("Privileged + User" Rows)
    hr = hResult[0]
    checkSum_Privileged = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr

    #Program Flash
    hr = ProgramFlash(hexImageSize)
    if (not SUCCEEDED(hr)): return hr

    #Verify Rows
    hr = PSoC4_VerifyFlash(hexImageSize)
    if (not SUCCEEDED(hr)): return hr
    
    #Protect All arrays
    hResult = pp.PSoC4_ProtectAll()
    hr = hResult[0]
    m_sLastError = hResult[0]
    if (not SUCCEEDED(hr)): return hr
    
    #Verify protection ChipLevelProtection and Protection data
    hResult = pp.PSoC4_VerifyProtect()
    hr = hResult[0]
    m_sLastError = hResult[0]
    if (not SUCCEEDED(hr)): return hr
    
    #CheckSum verification
    hResult = pp.PSoC4_CheckSum(0x8000) #CheckSum All Flash (Privileged + User)
    hr = hResult[0]
    checkSum_UserPrivileged = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    checkSum_User = checkSum_UserPrivileged - checkSum_Privileged #find checksum of User Flash rows
    
    hResult = pp.HEX_ReadChecksum()
    hr = hResult[0]
    hexChecksum = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    checkSum_User = checkSum_User & 0xFFFF
    hexChecksum = hexChecksum & 0xFFFF
    
    if (checkSum_User != hexChecksum):
        print "Mismatch of Checksum: Expected 0x%x, Got 0x%x" %(checkSum_User, hexChecksum)        
        return E_FAIL
    else:
        print "Checksum 0x%x" %(checkSum_User)    

    #Release PSoC3 device
    hResult = pp.DAP_ReleaseChip()
    hr = hResult[0]
    m_sLastError = hResult[1]
    
    return hr

def ProgramCARD():
    global m_sLastError
    # Open Port - get last (connected) port in the ports list
    hr = InitializePort()
    if (not SUCCEEDED(hr)): return hr
    
    # Set Hex File ##NEW CODE
    hResult = pp.HEX_ReadFile(os.getcwd() + "\CARD.cydsn\CortexM0\ARM_GCC_541\Release\CARD.hex")
    hr = hResult[0]
    hexImageSize = int(hResult[1])
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    
    #Read chip level protection from hex and check Chip Level Protection mode
    #If it is VIRGIN then don't allow Programming, since it can destroy chip
    hResult = pp.HEX_ReadChipProtection()
    hr = hResult[0]
    hex_chipProt = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    if (ord(hex_chipProt[0]) == CHIP_PROT_VIRGIN):
        m_sLastError = "Transition to VIRGIN is not allowed. It will destroy the chip. Please contact Cypress if you need this specifically."
        return E_FAIL

    # Set Acquire Mode
    pp.SetAcquireMode("Reset")

    #Acquire Device
    hResult = pp.DAP_Acquire()
    hr = hResult[0]
    m_sLastError = hResult[1]
    if (not SUCCEEDED(hr)): return hr
    
    #Check Hex File and Device compatibility
    fCompatibility = 0
    hResult = CheckHexAndDeviceCompatibility()
    hr = hResult[0]
    fCompatibility = hResult[1]    
    if (not SUCCEEDED(hr)): return hr
    if (fCompatibility == 0):
        m_sLastError = "The Hex file does not match the acquired device, please connect the appropriate device"
        return E_FAIL
    
    #Erase All
    hr = PSoC4_EraseAll()
    if (not SUCCEEDED(hr)): return hr

    #Find checksum of Privileged Flash. Will be used in calculation of User CheckSum later    
    hResult = pp.PSoC4_CheckSum(0x8000) #CheckSum All Flash ("Privileged + User" Rows)
    hr = hResult[0]
    checkSum_Privileged = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr

    #Program Flash
    hr = ProgramFlash(hexImageSize)
    if (not SUCCEEDED(hr)): return hr

    #Verify Rows
    hr = PSoC4_VerifyFlash(hexImageSize)
    if (not SUCCEEDED(hr)): return hr
    
    #Protect All arrays
    hResult = pp.PSoC4_ProtectAll()
    hr = hResult[0]
    m_sLastError = hResult[0]
    if (not SUCCEEDED(hr)): return hr
    
    #Verify protection ChipLevelProtection and Protection data
    hResult = pp.PSoC4_VerifyProtect()
    hr = hResult[0]
    m_sLastError = hResult[0]
    if (not SUCCEEDED(hr)): return hr
    
    #CheckSum verification
    hResult = pp.PSoC4_CheckSum(0x8000) #CheckSum All Flash (Privileged + User)
    hr = hResult[0]
    checkSum_UserPrivileged = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    checkSum_User = checkSum_UserPrivileged - checkSum_Privileged #find checksum of User Flash rows
    
    hResult = pp.HEX_ReadChecksum()
    hr = hResult[0]
    hexChecksum = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    checkSum_User = checkSum_User & 0xFFFF
    hexChecksum = hexChecksum & 0xFFFF
    
    if (checkSum_User != hexChecksum):
        print "Mismatch of Checksum: Expected 0x%x, Got 0x%x" %(checkSum_User, hexChecksum)        
        return E_FAIL
    else:
        print "Checksum 0x%x" %(checkSum_User)    

    #Release PSoC3 device
    hResult = pp.DAP_ReleaseChip()
    hr = hResult[0]
    m_sLastError = hResult[1]
    
    return hr

def UpgradeBlock():
    global m_sLastError

    # Open Port - get last (connected) port in the ports list
    hr = InitializePort()
    if (not SUCCEEDED(hr)): return hr

    # Set Acquire Mode
    pp.SetAcquireMode("Reset")

    #Acquire Device
    hResult = pp.DAP_Acquire()
    hr = hResult[0]
    m_sLastError = hResult[1]
    if (not SUCCEEDED(hr)): return hr

    #Write Block, use PSoC4_WriteRow() instead PSoC3_ProgramRow()
    hResult = pp.PSoC4_GetFlashInfo()
    hr = hResult[0]
    rowsPerArray = hResult[1]
    rowSize = hResult[2]
    m_sLastError = hResult[3]
    if (not SUCCEEDED(hr)): return hr

    writeData = [] #User and Config area of the Row (256+32)    
    for i in range(0, rowSize):
        writeData.append(i & 0xFF)
    data = array.array('B',writeData)
    rowID = rowSize - 1
    hResult = pp.PSoC4_WriteRow(rowID, buffer(data))
    hr = hResult[0]
    m_sLastError = hResult[1]
    if (not SUCCEEDED(hr)): return hr

    #Verify Row - only user area (without Config one)
    hResult = pp.PSoC4_ReadRow(rowID)
    hr = hResult[0]
    readData = hResult[1]
    m_sLastError = hResult[2]
    if (not SUCCEEDED(hr)): return hr
    
    for i in range(0, len(readData)):  #check 128 bytes        
        if (ord(readData[i]) != writeData[i]):
            hr = E_FAIL
            break
        
    if (not SUCCEEDED(hr)):
        m_sLastError = "Verification of User area failed!"
        return hr

    #Release PSoC4 chip
    hResult = pp.DAP_ReleaseChip()
    hr = hResult[0]
    m_sLastError = hResult[1]
    
    return hr

def Execute(program):  
    if (program == "ATM" or program == "BOTH"):
        print "Programming ATM..."
        hr = OpenPort()
        if (not SUCCEEDED(hr)): return hr
        hr = ProgramHSM()
        ClosePort()
        if(SUCCEEDED(hr)):
            pass
        else:
            return hr
    if (program == "CARD" or program == "BOTH"):    
        print "Programming CARD..."
        hr = OpenPort2()
        if (not SUCCEEDED(hr)): return hr
        hr = ProgramCARD()
        ClosePort()
    #hr = UpgradeBlock()
    return hr

def BuildAll():
    #Note this requires the the workspace to be in the same directory as the cmd running this script
    #For Windows-x32 Use the following
    #subprocess.call([r"C:\Program Files\Cypress\PSoC Creator\4.0\PSoC Creator\bin\cyprjmgr.exe",  "-wrk", "ectf-workspace.cywrk" , "-build"], shell=True)
    #For Windows-x64 Use the following
    subprocess.call([r"C:\Program Files (x86)\Cypress\PSoC Creator\4.1\PSoC Creator\bin\cyprjmgr.exe", "-ol", "High", "-c", "Release", "-wrk", "ectf-workspace.cywrk" , "-build"], shell=True)

    #If using a newer version of PSoC Creator change the number 4.0 to the current version number.

#Begin main program
#Use Version Independent Prog ID to instantiate COM-object
pp = win32com.client.Dispatch("PSoCProgrammerCOM.PSoCProgrammerCOM_Object")
#For version dependent Prog ID use below commented line, but update there COM-object version (e.g. 14)
#pp = win32com.client.Dispatch("PSoCProgrammerCOM.PSoCProgrammerCOM_Object.14")
def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('target', type=str,
                        help='Target for programming either ATM, CARD, or BOTH')

    # print "Please check the BuildAll function to ensure the correct .exe is being called."

    args = parser.parse_args()

    while args.target != "ATM" and args.target != "CARD" and args.target != "BOTH":
        print "Invalid input... Which devices are being programmed? ATM, CARD, or BOTH?"
        args.target = raw_input()
        if (args.target == "BOTH"):
            print "WARNING: Programming BOTH will require 2 MiniProg3's to be used at the same time."
            check = raw_input("Do you wish to continue? (yes/no)")
            if (check == "yes"):
                break
            else:
                args.target = ""

    print "Building Code"
    builder = threading.Thread(target=BuildAll)
    builder.start()
    while builder.isAlive():
        pass

    print "\nProgram All using COM-object interface only"
    hr = Execute(args.target)
    if (SUCCEEDED(hr)):
        strin = "Succeeded!"
    else:
        strin = "Failed! " + m_sLastError
    print strin
    raw_input("Press Enter to exit")
    #End main function



if __name__ == '__main__':
    main()

