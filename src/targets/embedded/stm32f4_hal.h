#ifndef NYX_STM32F4_BSP_H
#define NYX_STM32F4_BSP_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// --- STM32F4 Memory Map & MMIO Base Registers ---
#define STM32F4_PERIPH_BASE     (0x40000000UL)
#define STM32F4_AHB1PERIPH_BASE (STM32F4_PERIPH_BASE + 0x00020000UL)
#define STM32F4_APB1PERIPH_BASE (STM32F4_PERIPH_BASE + 0x00000000UL)
#define STM32F4_APB2PERIPH_BASE (STM32F4_PERIPH_BASE + 0x00010000UL)

// RCC (Reset & Clock Control)
#define RCC_BASE                (STM32F4_AHB1PERIPH_BASE + 0x3800UL)
#define RCC_AHB1ENR             (*(volatile uint32_t*)(RCC_BASE + 0x30UL))
#define RCC_APB1ENR             (*(volatile uint32_t*)(RCC_BASE + 0x40UL))

// GPIO Port Struct (MODER, OTYPER, OSPEEDR, PUPDR, IDR, ODR, BSRR, LCKR, AF)
typedef struct {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
    volatile uint32_t IDR;
    volatile uint32_t ODR;
    volatile uint32_t BSRR;
    volatile uint32_t LCKR;
    volatile uint32_t AFR[2];
} STM32F4_GPIO_TypeDef;

#define GPIOA                   ((STM32F4_GPIO_TypeDef*)(STM32F4_AHB1PERIPH_BASE + 0x0000UL))
#define GPIOB                   ((STM32F4_GPIO_TypeDef*)(STM32F4_AHB1PERIPH_BASE + 0x0400UL))
#define GPIOC                   ((STM32F4_GPIO_TypeDef*)(STM32F4_AHB1PERIPH_BASE + 0x0800UL))
#define GPIOD                   ((STM32F4_GPIO_TypeDef*)(STM32F4_AHB1PERIPH_BASE + 0x0C00UL))

// USART2 (APB1)
typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t BRR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t CR3;
    volatile uint32_t GTPR;
} STM32F4_USART_TypeDef;

#define USART2                  ((STM32F4_USART_TypeDef*)(STM32F4_APB1PERIPH_BASE + 0x4400UL))

// --- Nyx Hardware Abstraction Layer Implementations for STM32F4 ---
extern "C" {

inline void nyx_stm32f4_gpio_enable_clock(STM32F4_GPIO_TypeDef* port) {
    if (port == GPIOA) RCC_AHB1ENR |= (1UL << 0);
    else if (port == GPIOB) RCC_AHB1ENR |= (1UL << 1);
    else if (port == GPIOC) RCC_AHB1ENR |= (1UL << 2);
    else if (port == GPIOD) RCC_AHB1ENR |= (1UL << 3);
}

// Map logical pin (0-15 = GPIOA, 16-31 = GPIOB, 32-47 = GPIOC, 48-63 = GPIOD)
inline STM32F4_GPIO_TypeDef* nyx_stm32f4_get_port(int64_t pin, uint8_t* pin_num) {
    if (pin < 0 || pin > 63) return nullptr;
    if (pin >= 48) { *pin_num = (uint8_t)(pin - 48); return GPIOD; }
    if (pin >= 32) { *pin_num = (uint8_t)(pin - 32); return GPIOC; }
    if (pin >= 16) { *pin_num = (uint8_t)(pin - 16); return GPIOB; }
    *pin_num = (uint8_t)pin;
    return GPIOA;
}

inline void nyx_hal_gpio_mode(int64_t pin, int64_t mode) {
    uint8_t p = 0;
    STM32F4_GPIO_TypeDef* port = nyx_stm32f4_get_port(pin, &p);
    if (!port) return;
    nyx_stm32f4_gpio_enable_clock(port);
    
    // Clear 2-bit mode field
    port->MODER &= ~(3UL << (p * 2));
    if (mode == 1) {
        // Output mode (01)
        port->MODER |= (1UL << (p * 2));
    } else if (mode == 2) {
        // Input Pull-Up (mode 00 + PUPDR 01)
        port->PUPDR &= ~(3UL << (p * 2));
        port->PUPDR |= (1UL << (p * 2));
    } else if (mode == 3) {
        // Input Pull-Down (mode 00 + PUPDR 10)
        port->PUPDR &= ~(3UL << (p * 2));
        port->PUPDR |= (2UL << (p * 2));
    }
}

inline void nyx_hal_gpio_write(int64_t pin, int64_t val) {
    uint8_t p = 0;
    STM32F4_GPIO_TypeDef* port = nyx_stm32f4_get_port(pin, &p);
    if (!port) return;
    if (val) {
        port->BSRR = (1UL << p);       // Atomic Bit Set
    } else {
        port->BSRR = (1UL << (p + 16)); // Atomic Bit Reset
    }
}

inline int64_t nyx_hal_gpio_read(int64_t pin) {
    uint8_t p = 0;
    STM32F4_GPIO_TypeDef* port = nyx_stm32f4_get_port(pin, &p);
    if (!port) return 0;
    return (port->IDR & (1UL << p)) ? 1 : 0;
}

// Atomic BSRR-based toggle avoiding read-modify-write race conditions
inline void nyx_hal_gpio_toggle(int64_t pin) {
    uint8_t p = 0;
    STM32F4_GPIO_TypeDef* port = nyx_stm32f4_get_port(pin, &p);
    if (!port) return;
    if (port->ODR & (1UL << p)) {
        port->BSRR = (1UL << (p + 16)); // Atomic Reset
    } else {
        port->BSRR = (1UL << p);        // Atomic Set
    }
}

// USART2 Driver on PA2(TX) / PA3(RX) with proper AFR 4-bit masking
inline void nyx_hal_serial_init(int64_t baud) {
    // 1. Enable GPIOA and USART2 Clocks
    RCC_AHB1ENR |= (1UL << 0);
    RCC_APB1ENR |= (1UL << 17);
    
    // 2. Configure PA2 (TX) and PA3 (RX) as Alternate Function AF7
    GPIOA->MODER &= ~((3UL << 4) | (3UL << 6));
    GPIOA->MODER |= ((2UL << 4) | (2UL << 6));
    
    // Clear 4-bit AF fields first then write AF7
    GPIOA->AFR[0] &= ~((0xFUL << 8) | (0xFUL << 12));
    GPIOA->AFR[0] |= ((7UL << 8) | (7UL << 12));
    
    // 3. Set Baudrate (Assuming 16 MHz HSI clock: 16000000 / 115200 = 138.88 -> 0x8A)
    USART2->BRR = (16000000UL + (baud / 2)) / baud;
    
    // 4. Enable Transmitter, Receiver, and USART
    USART2->CR1 = (1UL << 3) | (1UL << 2) | (1UL << 13);
}

inline void nyx_hal_serial_write_byte(int64_t b) {
    while (!(USART2->SR & (1UL << 7))); // Wait until TXE (Transmit Empty)
    USART2->DR = (uint8_t)b;
}

inline void nyx_hal_serial_write(const char* data) {
    if (!data) return;
    while (*data) {
        nyx_hal_serial_write_byte(*data++);
    }
}

inline int64_t nyx_hal_serial_read_byte() {
    while (!(USART2->SR & (1UL << 5))); // Wait until RXNE (Read Not Empty)
    return (int64_t)(USART2->DR & 0xFF);
}

inline bool nyx_hal_serial_available() {
    return (USART2->SR & (1UL << 5)) != 0;
}

inline void delay_ms(int ms) {
    for (int i = 0; i < ms; i++) {
        for (int j = 0; j < 3195; j++) {
            __asm__ volatile("nop");
        }
    }
}

} // extern "C"

#endif // NYX_STM32F4_BSP_H