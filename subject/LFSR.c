#include <msp430.h> 
#include <stdint.h>

unsigned long long lfsr = 0xACE1ACE1ACE1ACE1ULL;  // 64-bit seed
uint16_t errorFlag = 0; //made the flag more general, will be useful in blinkPattern() function

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
void blinkingLEDPattern(){
    switch (errorFlag) {
        case 1: 
            for (int i = 0; i < 3; ++i) {
                P1OUT |= BIT2; // connect to pin 16 of subject
                __delay_cycles(100000);
                P1OUT &= ~BIT2;
                __delay_cycles(100000);
            }
            break;

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

    // Bitflip LED Setup
    P1DIR |= BIT0;
    P1OUT &= ~BIT0;

    // Heartbeat Setup (connect to pin 15 of subject)
    P1DIR |= BIT1;
    P1OUT &= ~BIT1;

    // Error LED Setup (connect to pin 16 of subject)
    P1DIR |= BIT2;
    P1OUT &= ~BIT2;

    // This will let us check the reason for reset before proceeding with the program
    resetCheck();
    while (1) {
        P1OUT ^= BIT1;  // Toggle heartbeat LED

        unsigned long long bit = ((lfsr >> 0) ^
                                  (lfsr >> 1) ^
                                  (lfsr >> 3) ^
                                  (lfsr >> 4)) & 1;
        lfsr = (lfsr >> 1) | (bit << 63);  // Shift full 64-bit range

        detectBitFlips(lfsr);
        blinkingLEDPattern();
        P1OUT ^= BIT1;
    }
}
