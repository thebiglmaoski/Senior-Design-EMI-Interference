#include <msp430.h> 
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define allocatedSize 2

// starting and ending address of each RAM Sector (see page 45 of the MSP430F5308 datasheet for table)

//sector 0 of RAM (datsheet says 0x002BFF to 0x002400, but we'll access memory from 0x002400 to 0x002BFF)
#define startAddress0 0x002400
#define endAddress0  0x002BFF

//sector 1 of RAM (datasheet says 0x0033FF to 0x002C00, but we'll access memory from 0x002C00 to 0x0033FF)
#define startAddress1 0x002C00
#define endAddress1 0x0033FF

//sector 7 of RAM (datasheet says 0x0023FF to 0x001C00 but we'll access memory from 0x001C00 to 0x0023FF)
#define startAddress7 0x001C00
#define endAddress7 0x0023FF


#define STACK_CANARY_ADDR  0x001C00 //variable initialized at the top of the stack, which is the highest valid ram address
unsigned long long lfsr = 0xACE1ACE1ACE1ACE1ULL;  // 64-bit seed
uint16_t errorFlag = 0; //made the flag more general, will be useful in blinkPattern() function
uint16_t bitflipFound = 0; //will be used in checkRAM() and memoryAllocation() as these functions maintained heartbeat


/* this function will iterate through each RAM sector's address, setting each memory location to 0.
If there's a more efficient way of zeroing out RAM, feel free to modify this function
*/
void zeroOutRAM(uint16_t* startAddress, uint16_t* endAddress){

    // this checks if we're writing to an invalid address (might of been why zeroOutRAM wasn't behaving as expected during testing)
    if ((uint16_t)startAddress < 0x001C00 || (uint16_t)endAddress > 0x0033FF || startAddress > endAddress || !startAddress || !endAddress) {
        return;
    }

    __disable_interrupt();
    
    while (startAddress <= endAddress) {
        *startAddress = 0x0000;
        startAddress += 1;
   }

    __enable_interrupt();
    
}

//after zeroing out the RAM sectors, this function will check each memory space to see if theres a non-zero value. if so, a bitflip occured
void checkRAM(uint16_t* startAddress, uint16_t* endAddress){

    bitflipFound = 0;
    // this checks if we're reading an invalid address
   if ((uint16_t)startAddress < 0x001C00 || (uint16_t)endAddress > 0x0033FF || startAddress > endAddress || !startAddress || !endAddress) {
        return;
    }
    
    while (startAddress <= endAddress) {
        if (*startAddress != 0) {
           bitflipFound = 1;
        }
         startAddress += 1;
   }

    if (!(P1OUT & BIT1) && bitflipFound){
        P1OUT |= BIT1;
}

/* This function allocates 2 bytes (16 bits) of memory where each space is initialized to 0 via calloc().
While iterating through the memory buffer, if theres a non-zero memory space then a bitflip has occured
and the bitflip LED will light up (Idea was inspired by the reference github in #software).
*/

void memoryAllocation(){

    unsigned char* memoryBuffer = (unsigned char*) calloc(allocatedSize, sizeof(unsigned char));
    int i = 0;
    bitflipFound = 0;
    
    if (memoryBuffer == NULL) {
        return;
    }



    for (i = 0; i < allocatedSize; ++i){
        if (memoryBuffer[i] != 0) {
            bitflipFound = 1;
        }
    }

    if (!(P1OUT & BIT1) && bitflipFound){
        P1OUT |= BIT1;
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
        P1OUT |= BIT1; // Indicate an error (connect to pin 14 of the subject)
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
                P1OUT |= BIT0; // connect to pin 16 of subject
                __delay_cycles(100000);
                P1OUT &= ~BIT0;
                __delay_cycles(100000);
            }
            break;
        // other errors will be 1 long blink
        case 2:
            P1OUT |= BIT0;
            __delay_cycles(600000);
            P1OUT &= ~BIT0;
            __delay_cycles(600000);
            break;

        default:
            P1OUT &= ~BIT0;
            break;
    }
}


void checkStackIntegrity() {
    if (*(volatile uint32_t*)STACK_CANARY_ADDR != 0xDEADBEEF) { //check if the address is kept the same
        P1OUT |= BIT1;  // Stack corruption detected, flash led
    }
}


/*calculates a simple CRC by XOR-ing values from a given memory range
 starts at the provided memory address and moves backward, updating the crc variable until it reaches the end address
The checkFlashIntegrity function then compares the computed CRC value with a predefined expected CRC*/
uint32_t computeCRC(uint32_t* start, uint32_t* end) {
      uint32_t crc = 0;
      while (start <= end) {
          crc ^= *start;
          start -= 1;
      }
      return crc;
  }

  void checkFlashIntegrity() {
      static uint32_t expected_crc = 0x12345678;  // Precomputed CRC value
      if (computeCRC((uint32_t*) 0xFFFF, (uint32_t*) 0xC000) != expected_crc) {
          P1OUT |= BIT1;  // Instruction memory corruption detected
      }
  }
 //end CRC section

/*
 we define a structure to store the values of critical CPU registers.
 The saveRegisters function uses inline assembly to store specific CPU registers into the saved_registers structure.
 The checkRegisters function then compares the current register values with the previously saved ones using memcmp.
 */
  typedef struct {
      uint16_t SR;
      uint16_t R4;
      uint16_t R5;
      uint16_t R6;
      uint16_t R7;
      uint16_t R8;
      uint16_t R9;
      uint16_t R10;
      uint16_t R11;
  } CPU_Registers;

  volatile CPU_Registers saved_registers;

  void saveRegisters() {
      saved_registers.SR = __get_SR_register();  // Save Status Register

      saved_registers.R4 = 0;  // Placeholder
      saved_registers.R5 = 0;  // Placeholder
      saved_registers.R6 = 0;  // Placeholder
      saved_registers.R7 = 0;  // Placeholder
      saved_registers.R8 = 0;  // Placeholder
      saved_registers.R9 = 0;  // Placeholder
      saved_registers.R10 = 0; // Placeholder
      saved_registers.R11 = 0; // Placeholder
  }

  void checkRegisters() {
      CPU_Registers current_registers;
      saveRegisters();  // Store the current state before comparison

      if (memcmp((const void*)&current_registers, (const void*)&saved_registers, sizeof(CPU_Registers)) != 0) {
          P1OUT |= BIT1;  // Indicate corruption
      }
  }

//end register check section



  int main(void) {
      WDTCTL = WDTPW | WDTHOLD;   // Stop Watchdog Timer

// UCSCTL5 register lets us manage the dividers of ACLK, SMCLK, and MCLK (see page 180 of the MSP430x5xx and MSP430x6xx family user guide). 
// DIVM_3 divides MCLK ( ~8 MHz) by 8, making MCLK now ~1MHz 
      UCSCTL5 = DIVM_3; 

      // Bitflip LED Setup (connect to pin 15 of subject)
      P1DIR |= BIT1;
      P1OUT &= ~BIT1;

      // Heartbeat Setup (connect to pin 16 of subject)
      P1DIR |= BIT2;
      P1OUT &= ~BIT2;

      // Error LED Setup (connect to pin 14 of subject)
      P1DIR |= BIT0;
      P1OUT &= ~BIT0;


      // Initialize RAM sectors 0, 1, and 7 to be 0
     zeroOutRAM((uint16_t*)startAddress0, (uint16_t*)endAddress0);
     zeroOutRAM((uint16_t*)startAddress1, (uint16_t*)endAddress1);
      zeroOutRAM((uint16_t*)startAddress7, (uint16_t*)endAddress7);

     // *(volatile uint32_t*)STACK_CANARY_ADDR = 0xDEADBEEF;

      // Check reset cause before proceeding
      resetCheck();

      P1OUT |= BIT2;
      while (1) {
          P1OUT ^= BIT2;  // Toggle heartbeat LED

          // Update LFSR for bit-flip detection
        /* unsigned long long bit = ((lfsr >> 0) ^
                                    (lfsr >> 1) ^
                                    (lfsr >> 3) ^
                                    (lfsr >> 4)) & 1;
          lfsr = (lfsr >> 1) | (bit << 63);  // Shift full 64-bit range
          */

          // Perform integrity checks



        checkRAM((uint16_t*)startAddress0, (uint16_t*)endAddress0);
        // after checking sector 0 of RAM, the bitflip flag resets to 0 for next RAM check
        if (bitflipFound == 1){
            bitflipFound = 0;
        }
          
        checkRAM((uint16_t*)startAddress1, (uint16_t*)endAddress1);
          // after checking sector 1 of RAM, the bitflip flag resets to 0 for next RAM check
        if (bitflipFound == 1){
            bitflipFound = 0;
        }
          
        checkRAM((uint16_t*)startAddress7, (uint16_t*)endAddress7);
          // after checking sector 7 of RAM, the bitflip flag resets to 0 for next RAM check
        if (bitflipFound == 1){
            bitflipFound = 0;
        }
        //  detectBitFlips(lfsr);
          
        memoryAllocation();
        // after checking heap, the bitflip flag resets to 0 for next RAM check
        if (bitflipFound == 1){
            bitflipFound = 0;
        }

          //checkStackIntegrity();  // Check for stack corruption
          //checkFlashIntegrity();  // Check flash memory integrity
        // checkRegisters();       // Check CPU register integrity

       //  blinkPattern();  // Handle any detected errors with LED patterns
          P1OUT ^= BIT2;
         __delay_cycles(500000);  // Small delay between iterations
      }
  }
