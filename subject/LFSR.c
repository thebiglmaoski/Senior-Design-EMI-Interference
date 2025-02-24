#include <msp430.h> 
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

#define allocatedSize 8

// starting and ending address of each RAM Sector (see page 45 of the MSP430F5308 datasheet for table)

//sector 0 of RAM (datsheet says 0x002BFF to 0x002400, but we'll access memory from 0x002400 to 0x002BFF)
#define startAddress0 0x002400 
#define endAddress0 0x002BFF

//sector 1 of RAM (datasheet says 0x0033FF to 0x002C00, but we'll access memory from 0x002C00 to 0x0033FF)
#define startAddress1 0x002C00 
#define endAddress1 0x0033FF 

//sector 7 of RAM (datasheet says 0x0023FF to 0x001C00 but we'll access memory from 0x001C00 to 0x0023FF)
#define startAddress7 0x001C00 
#define endAddress7 0x0023FF


unsigned long long lfsr = 0xACE1ACE1ACE1ACE1ULL;  // 64-bit seed
uint16_t errorFlag = 0; //made the flag more general, will be useful in blinkPattern() function


/* this function will iterate through each RAM sector's address, setting each memory location to 0.
If there's a more efficient way of zeroing out RAM, feel free to modify this function
*/
void zeroOutRAM(uint16_t* startAddress, uint16_t* endAddress){

     while (startAddress <= endAddress) {
        *startAddress = 0;
        startAddress += 1;
   }
}

//after zeroing out the RAM sectors, this function will check each memory space to see if theres a non-zero value. if so, a bitflip occured
void checkRAM(uint16_t* startAddress, uint16_t* endAddress){
      
   while (startAddress <= endAddress) {
        if (*startAddress != 0) {
           P1OUT |= BIT0;
        }

         startAddress += 1;   
   }
}

/* This function allocates 8 bytes (64 bits) of memory where each space is initialized to 0 via calloc().
While iterating through the memory buffer, if theres a non-zero memory space then a bitflip has occured
and the bitflip LED will light up (Idea was inspired by the reference github in #software).
*/

void memoryAllocation(){

    unsigned char* memoryBuffer = (unsigned char*) calloc(allocatedSize, sizeof(unsigned char));
    int i = 0;

    if (memoryBuffer == NULL) {
        return;
    }



    for (i = 0; i < allocatedSize; ++i){
        if (memoryBuffer[i] != 0) {
            P1OUT |= BIT0;
        }
    }

    free(memoryBuffer);
}




void detectBitFlips(unsigned long long actual_value) {
    static unsigned long long expected_lfsr = 0xACE1ACE1ACE1ACE1ULL;
    unsigned long long expected_bit = ((expected_lfsr >> 0) ^
                                       (expected_lfsr >> 1) ^
                                       (expected_lfsr >> 3) ^
                                       (expected_lfsr >> 4)) & 1;
    unsigned long long new_expected = (expected_lfsr >> 1) | (expected_bit << 63);

    if (new_expected != actual_value) {  // Compare full 64-bit values
        P1OUT |= BIT0; // Indicate an error (connect to pin 14 of the subject)
    }

    expected_lfsr = new_expected;
}

/* this function will read the value of the sysrstiv register (provides information on what caused reset)
and errorFlag will be set to a value corresponding to the reset cause (i.e 1 for brownout, 2 for other errors).
If needed, we can expand resetCheck() to check for other specific events besides brownout
*/
void resetCheck(){

    /*this accounts for the edge case where the register value is 0x00 (no reset), we want the errorFlag to be 0 here.
    otherwise, it would fall under the else condition and set errorFlag to 2.
    */

    if (SYSRSTIV == 0x00) {
        errorFlag = 0;
    }

   else if (SYSRSTIV == 0x02) { // Check for brownout reset
        errorFlag = 1; // Set errorFlag to 1 to indicate a brownout error
    }

    else {
        errorFlag = 2; // Set errorFlag to 2 to indicate other errors
    }
}

/* created a separate function to help identify reason for reset. Feel free to change the pattern of blinks
but currently, brownout will be 3 rapid blinks and other errors will be 1 long blink.

*/
void blinkPattern(){

    int i = 0;

    switch (errorFlag) {
        // brownout should be 3 quick blinks
        case 1:
            for (i = 0; i < 2; ++i) {
                P1OUT |= BIT2; // connect to pin 16 of subject
                __delay_cycles(100000);
                P1OUT &= ~BIT2;
                __delay_cycles(100000);
            }
            break;
        // other errors will be 1 long blink
        case 2:
            P1OUT |= BIT2;
            __delay_cycles(600000);
            P1OUT &= ~BIT2;
            __delay_cycles(600000);
            break;

        default:
            P1OUT &= ~BIT2;
            break;
    }
}


int main(void) {
    WDTCTL = WDTPW | WDTHOLD;   // Stop Watchdog Timer

    UCSCTL5 = DIVM_5;

    // Bitflip LED Setup (connect to pin 14 of subject)
    P1DIR |= BIT0;
    P1OUT &= ~BIT0;

    // Heartbeat Setup (connect to pin 15 of subject)
    P1DIR |= BIT1;
    P1OUT &= ~BIT1;

    // Error LED Setup (connect to pin 16 of subject)
    P1DIR |= BIT2;
    P1OUT &= ~BIT2;

    // initializing RAM sectors 0, 1, and 7 to be 0
     zeroOutRAM((uint16_t*)startAddress0, (uint16_t*)endAddress0); 
     zeroOutRAM((uint16_t*)startAddress1, (uint16_t*)endAddress1);
     zeroOutRAM((uint16_t*)startAddress7, (uint16_t*)endAddress7);

    // This will let us check the reason for reset before proceeding with the program
    resetCheck();
    while (1) {
        P1OUT ^= BIT1;  // Toggle heartbeat LED

        unsigned long long bit = ((lfsr >> 0) ^
                                  (lfsr >> 1) ^
                                  (lfsr >> 3) ^
                                  (lfsr >> 4)) & 1;
        lfsr = (lfsr >> 1) | (bit << 63);  // Shift full 64-bit range
       
       checkRAM((uint16_t*)startAddress0, (uint16_t*)endAddress0);
       checkRAM((uint16_t*)startAddress1, (uint16_t*)endAddress1);
       checkRAM((uint16_t*)startAddress7, (uint16_t*)endAddress7);
        
       detectBitFlips(lfsr);

       memoryAllocation();

       blinkPattern();


        P1OUT ^= BIT1;


    }
}
