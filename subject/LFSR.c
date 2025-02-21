#include <msp430.h> 
#include <stdint.h>

unsigned long long lfsr = 0xACE1ACE1ACE1ACE1ULL;  // 64-bit seed
uint16_t brownoutFlag = 0;

void detectBitFlips(unsigned long long actual_value) {
    static unsigned long long expected_lfsr = 0xACE1ACE1ACE1ACE1ULL;
    unsigned long long expected_bit = ((expected_lfsr >> 0) ^
                                       (expected_lfsr >> 1) ^
                                       (expected_lfsr >> 3) ^
                                       (expected_lfsr >> 4)) & 1;
    unsigned long long new_expected = (expected_lfsr >> 1) | (expected_bit << 63);

    if (new_expected != actual_value) {  // Compare full 64-bit values
        P1OUT |= BIT1; // Indicate an error
    }

    expected_lfsr = new_expected;
}

void resetCheck(){
    if (SYSRSTIV == 0x02) { // Check for brownout reset
        P1OUT |= BIT4; // Indicate brownout event
    } else {
        P1OUT |= BIT5; // Non-brownout reset
    }
}


int main(void) {
    WDTCTL = WDTPW | WDTHOLD;   // Stop Watchdog Timer

    UCSCTL5 = DIVM_5;

    // ACLK Setup
    P1DIR |= BIT0;
    P1SEL |= BIT0;

    // Heartbeat Setup
    P1DIR |= BIT2;
    P1OUT &= ~BIT2;

    // LED Setup
    P1DIR |= BIT1;
    P1OUT &= ~BIT1;

    P1OUT |= BIT2;
    while (1) {
        P1OUT ^= BIT2;  // Toggle heartbeat LED

        unsigned long long bit = ((lfsr >> 0) ^
                                  (lfsr >> 1) ^
                                  (lfsr >> 3) ^
                                  (lfsr >> 4)) & 1;
        lfsr = (lfsr >> 1) | (bit << 63);  // Shift full 64-bit range

        detectBitFlips(lfsr);

        P1OUT ^= BIT2;
    }
}
