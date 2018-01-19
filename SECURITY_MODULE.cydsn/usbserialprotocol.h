/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/
#ifndef USB_SERIAL_PROTOCOL_H
#define USB_SERIAL_PROTOCOL_H

#include "project.h"

#define SYNC_NORM 0
#define SYNC_PROV 1
    
/*
 * Blocking function that returns the first character  placed on DB_UART
 */
uint8 getValidByte();  


/*
 * Sends the first size bytes of message to the USB-SERIAL
 * Returns response byte from USB
 */
int pushMessage(const uint8 message[], uint8 size);


/*
 * Receives a message form the USB-SERIAL and places the data in message
 * Returns length of pulled message
 */
uint8 pullMessage(uint8 message[]);


/*
 * Blocking function that synchronizes connection with ATM
 */
void syncConnection(int prov);


#endif
/* [] END OF FILE */
