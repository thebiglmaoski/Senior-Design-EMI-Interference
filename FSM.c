#include <msp430.h> 

typedef enum {ON, UNLOCKED, TESTING, LOCKED} MSPstates;

MSPstates MSPTESTER = ON;

unsigned int myValue = 0x0000000;
unsigned int previousValue = 0xFFFFFFFF;

void nextState(MSPstates *state) {
    if (*state == LOCKED) {
        *state = ON;
    } else {
        *state = (MSPstates)((int)(*state) + 1);
    }
}

void assignVal(MSPstates state) {
    previousValue = myValue; // Store old value to compare later for bit flips
    switch(state) {
        case ON:
            myValue = 0x0000000;
            break;
        case UNLOCKED:
            myValue = 0x0000001;
            break;
        case TESTING:
            myValue = 0x0000010;
            break;
        case LOCKED:
            myValue = 0x0000100;
            break;
    }
}

void detectBitFlips(MSPstates state) {
    unsigned int expectedCurrentValue = 0;
    unsigned int expectedPreviousValue = 0;

    switch(state) {
        case ON:
            expectedCurrentValue = 0x0000000;
            expectedPreviousValue = 0x0000100;
            break;
        case UNLOCKED:
            expectedCurrentValue = 0x0000001;
            expectedPreviousValue = 0x0000000;
            break;
        case TESTING:
            expectedCurrentValue = 0x0000010;
            expectedPreviousValue = 0x0000001;
            break;
        case LOCKED:
            expectedCurrentValue = 0x0000100;
            expectedPreviousValue = 0x0000010;
            break;
    }

    if (myValue != expectedCurrentValue || previousValue != expectedPreviousValue) {
        P1OUT |= BIT1; // Turn on an LED to indicate error
        //future goal to throw interrupt here, do some sort of logging
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

    // Heartbeat Setup
    P1DIR |= BIT2;
    P1OUT &= ~BIT2;

    // LED Setup
    P1DIR |= BIT1;
    P1OUT &= ~BIT1;

    while(1) {
        P1OUT ^= BIT2;
        nextState(&MSPTESTER);
        assignVal(MSPTESTER);
        detectBitFlips(MSPTESTER);
        P1OUT ^= BIT2;

    }
}
