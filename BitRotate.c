#include <msp430.h>
#include <stdint.h>


void detectBitFlips(uint16_t actual, uint16_t expected) {
    if (actual != expected) {
        P1OUT |= BIT1;
        // Future goal: Trigger an interrupt, log the error, etc.
    } else {
        P1OUT &= ~BIT1;
    }
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

    // LED Setup
    P1DIR |= BIT1;
    P1OUT &= ~BIT1;

    // Heartbeat Setup
    P1DIR |= BIT2;
    P1OUT &= ~BIT2;

    uint16_t actualPattern   = 0x0001;
    uint16_t expectedPattern = 0x0001;

    while (1) {
        P1OUT ^= BIT2;

        actualPattern = (actualPattern << 1) | (actualPattern >> 15);
        expectedPattern = (expectedPattern << 1) | (expectedPattern >> 15);
        detectBitFlips(actualPattern, expectedPattern);

        P1OUT ^= BIT2;
    }
}
