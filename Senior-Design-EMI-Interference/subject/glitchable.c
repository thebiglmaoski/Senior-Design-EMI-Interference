// Based on NewAE Technology's "CW322 Simple EMFI Target - Glitchable Code"
#include <msp430.h> 
#include <stdint.h>

void glitch_loop(void)
{
    volatile uint32_t i, j;
    volatile uint32_t cnt;

    uint32_t OUTER_LOOP_CNT = 100;
    uint32_t INNER_LOOP_CNT = 100;

    while (1)
    {
        // Trigger Heartbeat
        P1OUT ^= BIT2;

        // Iterate and Add
        cnt = 0;
        for (i = 0; i < OUTER_LOOP_CNT; i++)
        {
            for (j = 0; j < INNER_LOOP_CNT; j++)
            {
                cnt++;
            }
        }

        // Check for Transient Fault
        if (i != OUTER_LOOP_CNT || j != INNER_LOOP_CNT
                || cnt != (OUTER_LOOP_CNT * INNER_LOOP_CNT))
        {
            // Trigger Pin when Fault Occurred
            P1OUT |= BIT0;
            __delay_cycles(500000);
            P1OUT &= ~BIT0;
        }
    }
}

int main(void)
{
    // Stop Watchdog Timer
    WDTCTL = WDTPW | WDTHOLD;

    // Set MCLK Speed to Highest
    UCSCTL5 = DIVM_0;

    // Glitch Output Setup
    P1DIR |= BIT0;
    P1OUT &= ~BIT0;

    // Reset Output Setup
    P1DIR |= BIT1;
    P1OUT &= ~BIT1;

    // Heartbeat Output Setup
    P1DIR |= BIT2;
    P1OUT &= ~BIT2;

    // Check for Resets
//    volatile unsigned int reset = *(&SYSRSTIV);
    uint16_t reset_val = SYSRSTIV;
//    reset_val = 4;
    if (reset_val != SYSRSTIV_NONE)
    {
//        __delay_cycles(250000);
        switch (reset_val)
        {
        case SYSRSTIV_PMMKEY:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_PERF:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_KEYV:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_WDTKEY:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_WDTTO:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_DOPOR:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_SVMH_OVP:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_SVML_OVP:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_SVSH:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_SVSL:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_SECYV:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_LPM5WU:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_DOBOR:
            P1OUT |= BIT1;
            __delay_cycles(250000);
            P1OUT &= ~BIT1;
            __delay_cycles(250000);
        case SYSRSTIV_RSTNMI:
            P1OUT |= BIT1;
            __delay_cycles(100000);
            P1OUT &= ~BIT1;
            __delay_cycles(100000);

            // Check SYSSNIV
            uint16_t NMI_val = SYSSNIV;
            if (NMI_val != SYSSNIV_NONE) {
                switch (NMI_val)
                {
                case SYSSNIV_VLRHIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_VLRLIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_JMBOUTIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_JMBINIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_VMAIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_DLYHIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_DLYLIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_SVMHIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    __delay_cycles(100000);
                case SYSSNIV_SVMLIFG:
                    P1OUT |= BIT0;
                    __delay_cycles(100000);
                    P1OUT &= ~BIT0;
                    break;
                default:
                    P1OUT |= BIT0;
                    __delay_cycles(1000000);
                    P1OUT &= ~BIT0;
                }
            }

            if (NMI_val == SYSSNIV_VMAIFG)
            {
                // Trigger Pin when Fault Occurred
                P1OUT |= BIT0;
                __delay_cycles(500000);
                P1OUT &= ~BIT0;
            }
        case SYSRSTIV_BOR:
            P1OUT |= BIT1;
            __delay_cycles(100000);
            P1OUT &= ~BIT1;
            __delay_cycles(100000);
            P1OUT |= BIT1;
            __delay_cycles(100000);
            P1OUT &= ~BIT1;
            break;
        default:
            P1OUT |= BIT1;
            __delay_cycles(1000000);
            P1OUT &= ~BIT1;
        }
    }

    // ##### INCREASING EMI #####

    // Set remaining pins to floating inputs
    P6DIR &= ~(BIT0 | BIT1 | BIT2 | BIT3);
    P5DIR &= ~(BIT0 | BIT1 | BIT2 | BIT3 | BIT4 | BIT5);
    P4DIR &= ~(BIT0 | BIT1 | BIT2 | BIT3 | BIT4 | BIT5 | BIT6 | BIT7);
    P2DIR &= ~(BIT0);
    P1DIR &= ~(BIT3 | BIT4 | BIT5 | BIT6 | BIT7);
    // High outputs instead?

    // Allow for interrupts to freeze the program
    __enable_interrupt();

    // Enable peripherals that will not be used
    // UART
    // Timers
    // ADC
    // I2C
    // SPI
    // DAC

    // Initiate Infinite Actions
    glitch_loop();
}

