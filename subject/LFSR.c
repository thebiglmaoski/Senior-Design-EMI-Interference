#include <msp430.h> 
#include <stdint.h>

uint16_t lfsr = 0xACE1u;


void detectBitFlips(uint16_t actual_value) {
    static uint16_t expected_lfsr = 0xACE1u;
    uint16_t expected_bit = ((expected_lfsr >> 0) ^
                             (expected_lfsr >> 2) ^
                             (expected_lfsr >> 3) ^
                             (expected_lfsr >> 5)) & 1;
    uint16_t new_expected = (expected_lfsr >> 1) | (expected_bit << 15);

    if (actual_value != new_expected) {
        P1OUT |= BIT1;
    }

    /*else {
        P1OUT &= ~BIT1;
    }
*/
    expected_lfsr = new_expected;
}

int main(void) {
    WDTCTL = WDTPW | WDTHOLD;   // Stop Watchdog Timer

    // ACLK Setup
    P1DIR |= BIT0;
    P1SEL |= BIT0;

    // SMCLK Setup
    /*P1DIR |= BIT1;
    P1SEL |= BIT1;
    TA0CTL = MC_2 | ID_0 | TASSEL_2 | TACLR;
    TA0CCTL0 |= OUTMOD_4;*/

    // Heartbeat Setup
    P1DIR |= BIT2;
    P1OUT &= ~BIT2;

    // LED Setup
    P1DIR |= BIT1;
    P1OUT &= ~BIT1;


    P1OUT |= BIT2;
    while (1) {
        // Update the actual LFSR value using the taps: bits 0, 2, 3, and 5.
        P1OUT ^= BIT2;
        uint16_t bit = ((lfsr >> 0) ^ (lfsr >> 2) ^ (lfsr >> 3) ^ (lfsr >> 5)) & 1;
        lfsr = (lfsr >> 1) | (bit << 15);

        // Call the error detection function with the new LFSR value.
        detectBitFlips(lfsr);

        P1OUT ^= BIT2;
    }
}
