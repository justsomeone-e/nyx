#include <stdint.h>
#include <stddef.h>

extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

extern "C" int main(void);

// --- Standard ARM EABI Compliant Assembly Helpers (AAPCS) ---
extern "C" {

void* memcpy(void* dest, const void* src, size_t n) {
    uint8_t* d = (uint8_t*)dest;
    const uint8_t* s = (const uint8_t*)src;
    while (n--) *d++ = *s++;
    return dest;
}

void* memset(void* s, int c, size_t n) {
    uint8_t* p = (uint8_t*)s;
    while (n--) *p++ = (uint8_t)c;
    return s;
}

void __aeabi_memcpy4(void* dest, const void* src, size_t n) { memcpy(dest, src, n); }
void __aeabi_memcpy(void* dest, const void* src, size_t n) { memcpy(dest, src, n); }
void __aeabi_memclr4(void* dest, size_t n) { memset(dest, 0, n); }
void __aeabi_memclr(void* dest, size_t n) { memset(dest, 0, n); }

// Pure Thumb-2 Assembly __aeabi_uldivmod:
// Inputs:  r0:r1 = Numerator, r2:r3 = Denominator
// Outputs: r0:r1 = Quotient,  r2:r3 = Remainder
__attribute__((naked)) void __aeabi_uldivmod(void) {
    __asm__ volatile (
        "push {r4, r5, r6, r7, lr}\n"
        "cbz r2, .Lcheck_high_zero\n"
        "b .Lstart_div\n"
        ".Lcheck_high_zero:\n"
        "cbz r3, .Ldiv_by_zero\n"
        ".Lstart_div:\n"
        "mov r4, #0\n"          // Q_low
        "mov r5, #0\n"          // Q_high
        "mov r6, #0\n"          // R_low
        "mov r7, #0\n"          // R_high
        "mov lr, #64\n"         // 64 iterations
        ".Ldiv_loop:\n"
        "lsls r6, r6, #1\n"
        "orrs r6, r6, r7, lsr #31\n"
        "lsls r7, r7, #1\n"
        "orrs r6, r6, r1, lsr #31\n"
        "lsls r1, r1, #1\n"
        "orrs r1, r1, r0, lsr #31\n"
        "lsls r0, r0, #1\n"
        "subs r12, r6, r2\n"
        "sbcs r12, r7, r3\n"
        "blo .Lskip_sub\n"
        "subs r6, r6, r2\n"
        "sbc  r7, r7, r3\n"
        "adds r4, r4, #1\n"
        "adc  r5, r5, #0\n"
        ".Lskip_sub:\n"
        "subs lr, lr, #1\n"
        "bne .Ldiv_loop\n"
        "mov r0, r4\n"          // Return Quotient low
        "mov r1, r5\n"          // Return Quotient high
        "mov r2, r6\n"          // Return Remainder low
        "mov r3, r7\n"          // Return Remainder high
        "pop {r4, r5, r6, r7, pc}\n"
        ".Ldiv_by_zero:\n"
        "mov r0, #0\n"
        "mov r1, #0\n"
        "mov r2, #0\n"
        "mov r3, #0\n"
        "pop {r4, r5, r6, r7, pc}\n"
    );
}

__attribute__((naked)) void __aeabi_ldivmod(void) {
    __asm__ volatile (
        "push {r4, r5, r6, r7, lr}\n"
        "bl __aeabi_uldivmod\n"
        "pop {r4, r5, r6, r7, pc}\n"
    );
}

void Reset_Handler(void) {
    // 1. Copy initialized data from FLASH to SRAM
    uint32_t* src = &_sidata;
    uint32_t* dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }

    // 2. Zero-fill uninitialized BSS in SRAM
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }

    // 3. Jump to Nyx main application
    main();

    // 4. Trap infinite loop if main returns
    while (1) {
        __asm__ volatile("wfi");
    }
}

void Default_Handler(void) {
    while (1);
}

} // extern "C"

// ARM Cortex-M Vector Table
__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))(&_estack),
    Reset_Handler,
    Default_Handler, // NMI_Handler
    Default_Handler, // HardFault_Handler
    Default_Handler, // MemManage_Handler
    Default_Handler, // BusFault_Handler
    Default_Handler, // UsageFault_Handler
    0, 0, 0, 0,
    Default_Handler, // SVC_Handler
    Default_Handler, // DebugMon_Handler
    0,
    Default_Handler, // PendSV_Handler
    Default_Handler, // SysTick_Handler
};