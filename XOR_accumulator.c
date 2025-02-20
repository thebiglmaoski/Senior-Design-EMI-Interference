#include <msp430.h>
#include <stdint.h>


void detectBitFlips(uint16_t accumulator, uint16_t expected) {
    if (accumulator != expected) {
        P1OUT |= BIT2;

    } else {
        P1OUT &= ~BIT2;
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

    uint16_t accumulator = 0;
    const uint16_t mask = 0xBEEF;
    uint16_t expected = 0;

    while (1) {
        P1OUT ^= BIT2;


        accumulator ^= mask;
        expected ^= mask;

        detectBitFlips(accumulator, expected);

        _P1OUT ^= BIT2;
    }
}
