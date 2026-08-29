#include <stdint.h>
#include <stddef.h>

extern uint32_t _estack;
extern uint32_t _sidata;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;

extern "C" int main(void);

// --- ARM EABI Bare-Metal Intrinsics ---
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

void __aeabi_memcpy4(void* dest, const void* src, size_t n) {
    memcpy(dest, src, n);
}

void __aeabi_memcpy(void* dest, const void* src, size_t n) {
    memcpy(dest, src, n);
}

void __aeabi_memclr4(void* dest, size_t n) {
    memset(dest, 0, n);
}

void __aeabi_memclr(void* dest, size_t n) {
    memset(dest, 0, n);
}

struct uldivmod_result {
    uint64_t quot;
    uint64_t rem;
};

uldivmod_result __aeabi_uldivmod(uint64_t num, uint64_t den) {
    if (den == 0) return {0, 0};
    uint64_t quot = 0;
    uint64_t rem = 0;
    for (int i = 63; i >= 0; i--) {
        rem = (rem << 1) | ((num >> i) & 1);
        if (rem >= den) {
            rem -= den;
            quot |= (1ULL << i);
        }
    }
    return {quot, rem};
}

int64_t __aeabi_ldivmod(int64_t num, int64_t den) {
    if (den == 0) return 0;
    bool neg = (num < 0) ^ (den < 0);
    uint64_t u_num = num < 0 ? (uint64_t)(-num) : (uint64_t)num;
    uint64_t u_den = den < 0 ? (uint64_t)(-den) : (uint64_t)den;
    uldivmod_result res = __aeabi_uldivmod(u_num, u_den);
    return neg ? -(int64_t)res.quot : (int64_t)res.quot;
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