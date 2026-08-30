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
#define RCC_APB2ENR             (*(volatile uint32_t*)(RCC_BASE + 0x44UL))

#define NYX_STM32F4_CORE_CLOCK_HZ 16000000UL
#define NYX_STM32F4_IO_TIMEOUT    1000000UL

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

typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t CRCPR;
    volatile uint32_t RXCRCR;
    volatile uint32_t TXCRCR;
    volatile uint32_t I2SCFGR;
    volatile uint32_t I2SPR;
} STM32F4_SPI_TypeDef;

#define SPI1                    ((STM32F4_SPI_TypeDef*)(STM32F4_APB2PERIPH_BASE + 0x3000UL))

typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t OAR1;
    volatile uint32_t OAR2;
    volatile uint32_t DR;
    volatile uint32_t SR1;
    volatile uint32_t SR2;
    volatile uint32_t CCR;
    volatile uint32_t TRISE;
    volatile uint32_t FLTR;
} STM32F4_I2C_TypeDef;

#define I2C1                    ((STM32F4_I2C_TypeDef*)(STM32F4_APB1PERIPH_BASE + 0x5400UL))

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMPR1;
    volatile uint32_t SMPR2;
    volatile uint32_t JOFR1;
    volatile uint32_t JOFR2;
    volatile uint32_t JOFR3;
    volatile uint32_t JOFR4;
    volatile uint32_t HTR;
    volatile uint32_t LTR;
    volatile uint32_t SQR1;
    volatile uint32_t SQR2;
    volatile uint32_t SQR3;
    volatile uint32_t JSQR;
    volatile uint32_t JDR1;
    volatile uint32_t JDR2;
    volatile uint32_t JDR3;
    volatile uint32_t JDR4;
    volatile uint32_t DR;
} STM32F4_ADC_TypeDef;

#define ADC1                    ((STM32F4_ADC_TypeDef*)(STM32F4_APB2PERIPH_BASE + 0x2000UL))

typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCMR2;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
    volatile uint32_t RCR;
    volatile uint32_t CCR1;
    volatile uint32_t CCR2;
    volatile uint32_t CCR3;
    volatile uint32_t CCR4;
    volatile uint32_t BDTR;
    volatile uint32_t DCR;
    volatile uint32_t DMAR;
} STM32F4_TIM_TypeDef;

#define TIM2                    ((STM32F4_TIM_TypeDef*)(STM32F4_APB1PERIPH_BASE + 0x0000UL))
#define TIM3                    ((STM32F4_TIM_TypeDef*)(STM32F4_APB1PERIPH_BASE + 0x0400UL))
#define TIM4                    ((STM32F4_TIM_TypeDef*)(STM32F4_APB1PERIPH_BASE + 0x0800UL))
#define TIM5                    ((STM32F4_TIM_TypeDef*)(STM32F4_APB1PERIPH_BASE + 0x0C00UL))
#define TIM6                    ((STM32F4_TIM_TypeDef*)(STM32F4_APB1PERIPH_BASE + 0x1000UL))

#define NYX_NVIC_ISER           ((volatile uint32_t*)0xE000E100UL)
#define NYX_NVIC_ICER           ((volatile uint32_t*)0xE000E180UL)
#define NYX_NVIC_ISPR           ((volatile uint32_t*)0xE000E200UL)
#define NYX_NVIC_ICPR           ((volatile uint32_t*)0xE000E280UL)
#define NYX_NVIC_IPR            ((volatile uint8_t*)0xE000E400UL)

// --- Nyx Hardware Abstraction Layer Implementations for STM32F4 ---
extern "C" {

inline bool nyx_hal_string_equal(const char* left, const char* right) {
    if (!left || !right) return false;
    while (*left && *right) {
        if (*left != *right) return false;
        ++left;
        ++right;
    }
    return *left == *right;
}

// Resolve connector aliases from the selected board profile.  Unknown names
// return -1 instead of silently selecting a physical pin.
inline int64_t nyx_hal_board_pin(const char* name) {
#ifdef NYX_PIN_LED
    if (nyx_hal_string_equal(name, "LED")) return NYX_PIN_LED;
#endif
#ifdef NYX_PIN_BUTTON
    if (nyx_hal_string_equal(name, "BUTTON")) return NYX_PIN_BUTTON;
#endif
#ifdef NYX_PIN_UART_TX
    if (nyx_hal_string_equal(name, "UART_TX")) return NYX_PIN_UART_TX;
#endif
#ifdef NYX_PIN_UART_RX
    if (nyx_hal_string_equal(name, "UART_RX")) return NYX_PIN_UART_RX;
#endif
#ifdef NYX_PIN_SPI_SCK
    if (nyx_hal_string_equal(name, "SPI_SCK")) return NYX_PIN_SPI_SCK;
#endif
#ifdef NYX_PIN_SPI_MISO
    if (nyx_hal_string_equal(name, "SPI_MISO")) return NYX_PIN_SPI_MISO;
#endif
#ifdef NYX_PIN_SPI_MOSI
    if (nyx_hal_string_equal(name, "SPI_MOSI")) return NYX_PIN_SPI_MOSI;
#endif
#ifdef NYX_PIN_I2C_SDA
    if (nyx_hal_string_equal(name, "I2C_SDA")) return NYX_PIN_I2C_SDA;
#endif
#ifdef NYX_PIN_I2C_SCL
    if (nyx_hal_string_equal(name, "I2C_SCL")) return NYX_PIN_I2C_SCL;
#endif
#ifdef NYX_PIN_D0
    if (nyx_hal_string_equal(name, "D0")) return NYX_PIN_D0;
#endif
#ifdef NYX_PIN_D1
    if (nyx_hal_string_equal(name, "D1")) return NYX_PIN_D1;
#endif
#ifdef NYX_PIN_D2
    if (nyx_hal_string_equal(name, "D2")) return NYX_PIN_D2;
#endif
#ifdef NYX_PIN_D3
    if (nyx_hal_string_equal(name, "D3")) return NYX_PIN_D3;
#endif
#ifdef NYX_PIN_D4
    if (nyx_hal_string_equal(name, "D4")) return NYX_PIN_D4;
#endif
#ifdef NYX_PIN_D5
    if (nyx_hal_string_equal(name, "D5")) return NYX_PIN_D5;
#endif
#ifdef NYX_PIN_D6
    if (nyx_hal_string_equal(name, "D6")) return NYX_PIN_D6;
#endif
#ifdef NYX_PIN_D7
    if (nyx_hal_string_equal(name, "D7")) return NYX_PIN_D7;
#endif
#ifdef NYX_PIN_D8
    if (nyx_hal_string_equal(name, "D8")) return NYX_PIN_D8;
#endif
#ifdef NYX_PIN_D9
    if (nyx_hal_string_equal(name, "D9")) return NYX_PIN_D9;
#endif
#ifdef NYX_PIN_D10
    if (nyx_hal_string_equal(name, "D10")) return NYX_PIN_D10;
#endif
#ifdef NYX_PIN_D11
    if (nyx_hal_string_equal(name, "D11")) return NYX_PIN_D11;
#endif
#ifdef NYX_PIN_D12
    if (nyx_hal_string_equal(name, "D12")) return NYX_PIN_D12;
#endif
#ifdef NYX_PIN_D13
    if (nyx_hal_string_equal(name, "D13")) return NYX_PIN_D13;
#endif
#ifdef NYX_PIN_D14
    if (nyx_hal_string_equal(name, "D14")) return NYX_PIN_D14;
#endif
#ifdef NYX_PIN_D15
    if (nyx_hal_string_equal(name, "D15")) return NYX_PIN_D15;
#endif
#ifdef NYX_PIN_A0
    if (nyx_hal_string_equal(name, "A0")) return NYX_PIN_A0;
#endif
#ifdef NYX_PIN_A1
    if (nyx_hal_string_equal(name, "A1")) return NYX_PIN_A1;
#endif
#ifdef NYX_PIN_A2
    if (nyx_hal_string_equal(name, "A2")) return NYX_PIN_A2;
#endif
#ifdef NYX_PIN_A3
    if (nyx_hal_string_equal(name, "A3")) return NYX_PIN_A3;
#endif
#ifdef NYX_PIN_A4
    if (nyx_hal_string_equal(name, "A4")) return NYX_PIN_A4;
#endif
#ifdef NYX_PIN_A5
    if (nyx_hal_string_equal(name, "A5")) return NYX_PIN_A5;
#endif
    return -1;
}

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

inline bool nyx_stm32f4_gpio_config_alt(int64_t pin, uint8_t af, bool open_drain) {
    uint8_t p = 0;
    STM32F4_GPIO_TypeDef* port = nyx_stm32f4_get_port(pin, &p);
    if (!port || af > 15) return false;
    nyx_stm32f4_gpio_enable_clock(port);
    port->MODER = (port->MODER & ~(3UL << (p * 2))) | (2UL << (p * 2));
    port->OTYPER = (port->OTYPER & ~(1UL << p)) | ((open_drain ? 1UL : 0UL) << p);
    port->OSPEEDR = (port->OSPEEDR & ~(3UL << (p * 2))) | (3UL << (p * 2));
    port->PUPDR = (port->PUPDR & ~(3UL << (p * 2))) |
        ((open_drain ? 1UL : 0UL) << (p * 2));
    const uint32_t index = p / 8U;
    const uint32_t shift = (p % 8U) * 4U;
    port->AFR[index] = (port->AFR[index] & ~(0xFUL << shift)) | ((uint32_t)af << shift);
    return true;
}

inline bool nyx_stm32f4_gpio_config_analog(int64_t pin) {
    uint8_t p = 0;
    STM32F4_GPIO_TypeDef* port = nyx_stm32f4_get_port(pin, &p);
    if (!port) return false;
    nyx_stm32f4_gpio_enable_clock(port);
    port->MODER = (port->MODER & ~(3UL << (p * 2))) | (3UL << (p * 2));
    port->PUPDR &= ~(3UL << (p * 2));
    return true;
}

inline void nyx_hal_gpio_mode(int64_t pin, int64_t mode) {
    uint8_t p = 0;
    STM32F4_GPIO_TypeDef* port = nyx_stm32f4_get_port(pin, &p);
    if (!port) return;
    nyx_stm32f4_gpio_enable_clock(port);
    
    // Reset pin configuration before applying the requested mode.
    port->MODER &= ~(3UL << (p * 2));
    port->PUPDR &= ~(3UL << (p * 2));
    port->OTYPER &= ~(1UL << p);
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
inline bool nyx_hal_serial_init(int64_t baud) {
    if (baud <= 0) return false;
    const uint64_t divider = ((uint64_t)NYX_STM32F4_CORE_CLOCK_HZ + (uint64_t)baud / 2U) /
        (uint64_t)baud;
    if (divider == 0U || divider > 0xFFFFU) return false;

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
    USART2->BRR = (uint32_t)divider;
    
    // 4. Enable Transmitter, Receiver, and USART
    USART2->CR1 = (1UL << 3) | (1UL << 2) | (1UL << 13);
    return true;
}

inline bool nyx_hal_serial_write_byte(int64_t b) {
    uint32_t timeout = NYX_STM32F4_IO_TIMEOUT;
    while (!(USART2->SR & (1UL << 7)) && timeout > 0U) --timeout;
    if (timeout == 0U) return false;
    USART2->DR = (uint8_t)b;
    return true;
}

inline int64_t nyx_hal_serial_write(const char* data) {
    if (!data) return -1;
    int64_t written = 0;
    while (*data) {
        if (!nyx_hal_serial_write_byte(*data++)) return -2;
        ++written;
    }
    return written;
}

inline int64_t nyx_hal_serial_write_buffer(uintptr_t data, int64_t length) {
    if (length < 0 || (length > 0 && data == 0U)) return -1;
    const uint8_t* bytes = (const uint8_t*)data;
    for (int64_t index = 0; index < length; ++index) {
        if (!nyx_hal_serial_write_byte(bytes[index])) return -2;
    }
    return length;
}

inline int64_t nyx_hal_serial_read_buffer(uintptr_t data, int64_t capacity) {
    if (capacity < 0 || (capacity > 0 && data == 0U)) return -1;
    uint8_t* bytes = (uint8_t*)data;
    int64_t received = 0;
    while (received < capacity && (USART2->SR & (1UL << 5)) != 0U) {
        bytes[received++] = (uint8_t)(USART2->DR & 0xFFU);
    }
    return received;
}

inline int64_t nyx_hal_serial_read_byte() {
    while (!(USART2->SR & (1UL << 5))); // Wait until RXNE (Read Not Empty)
    return (int64_t)(USART2->DR & 0xFF);
}

inline bool nyx_hal_serial_available() {
    return (USART2->SR & (1UL << 5)) != 0;
}

inline void nyx_hal_irq_enable(int64_t irq) {
    if (irq < 0 || irq >= 240) return;
    NYX_NVIC_ISER[(uint32_t)irq / 32U] = 1UL << ((uint32_t)irq % 32U);
}

inline void nyx_hal_irq_disable(int64_t irq) {
    if (irq < 0 || irq >= 240) return;
    NYX_NVIC_ICER[(uint32_t)irq / 32U] = 1UL << ((uint32_t)irq % 32U);
}

inline void nyx_hal_irq_set_priority(int64_t irq, int64_t priority) {
    if (irq < 0 || irq >= 240) return;
    if (priority < 0) priority = 0;
    if (priority > 15) priority = 15;
    NYX_NVIC_IPR[(uint32_t)irq] = (uint8_t)((uint32_t)priority << 4U);
}

inline bool nyx_hal_irq_is_pending(int64_t irq) {
    if (irq < 0 || irq >= 240) return false;
    return (NYX_NVIC_ISPR[(uint32_t)irq / 32U] & (1UL << ((uint32_t)irq % 32U))) != 0;
}

inline void nyx_hal_irq_clear_pending(int64_t irq) {
    if (irq < 0 || irq >= 240) return;
    NYX_NVIC_ICPR[(uint32_t)irq / 32U] = 1UL << ((uint32_t)irq % 32U);
}

inline bool nyx_hal_spi_init(int64_t bus, int64_t frequency, int64_t mode) {
    const int64_t minimum_frequency = (int64_t)NYX_STM32F4_CORE_CLOCK_HZ / 256;
    const int64_t maximum_frequency = (int64_t)NYX_STM32F4_CORE_CLOCK_HZ / 2;
    if (
        bus != 1 || frequency < minimum_frequency || frequency > maximum_frequency ||
        mode < 0 || mode > 3
    ) return false;
    RCC_AHB1ENR |= (1UL << 0);
    RCC_APB2ENR |= (1UL << 12);
    nyx_stm32f4_gpio_config_alt(5, 5, false); // PA5: SPI1 SCK
    nyx_stm32f4_gpio_config_alt(6, 5, false); // PA6: SPI1 MISO
    nyx_stm32f4_gpio_config_alt(7, 5, false); // PA7: SPI1 MOSI

    uint32_t divisor = 2U;
    uint32_t br = 0U;
    while ((NYX_STM32F4_CORE_CLOCK_HZ / divisor) > (uint32_t)frequency && br < 7U) {
        divisor <<= 1U;
        ++br;
    }
    SPI1->CR1 = (1UL << 2) | (1UL << 9) | (1UL << 8) | (br << 3) |
        (((uint32_t)mode & 1U) << 0) | ((((uint32_t)mode >> 1U) & 1U) << 1);
    SPI1->CR2 = 0;
    SPI1->CR1 |= (1UL << 6);
    return true;
}

inline int64_t nyx_hal_spi_transfer(int64_t bus, int64_t value) {
    if (bus != 1 || !(SPI1->CR1 & (1UL << 6))) return -1;
    uint32_t timeout = NYX_STM32F4_IO_TIMEOUT;
    while (!(SPI1->SR & (1UL << 1)) && timeout > 0U) --timeout;
    if (timeout == 0U) return -2;
    *(volatile uint8_t*)&SPI1->DR = (uint8_t)value;
    timeout = NYX_STM32F4_IO_TIMEOUT;
    while (!(SPI1->SR & (1UL << 0)) && timeout > 0U) --timeout;
    if (timeout == 0U) return -3;
    const uint8_t received = *(volatile uint8_t*)&SPI1->DR;
    timeout = NYX_STM32F4_IO_TIMEOUT;
    while ((SPI1->SR & (1UL << 7)) && timeout > 0U) --timeout;
    return timeout == 0U ? -4 : (int64_t)received;
}

inline int64_t nyx_hal_spi_write_buffer(int64_t bus, uintptr_t data, int64_t length) {
    if (length < 0 || (length > 0 && data == 0U)) return -5;
    const uint8_t* bytes = (const uint8_t*)data;
    for (int64_t index = 0; index < length; ++index) {
        const int64_t result = nyx_hal_spi_transfer(bus, bytes[index]);
        if (result < 0) return result;
    }
    return length;
}

inline int64_t nyx_hal_spi_transfer_buffer(
    int64_t bus, uintptr_t transmit, uintptr_t receive, int64_t length
) {
    if (length < 0 || (length > 0 && (transmit == 0U || receive == 0U))) return -5;
    const uint8_t* tx = (const uint8_t*)transmit;
    uint8_t* rx = (uint8_t*)receive;
    for (int64_t index = 0; index < length; ++index) {
        const int64_t result = nyx_hal_spi_transfer(bus, tx[index]);
        if (result < 0) return result;
        rx[index] = (uint8_t)result;
    }
    return length;
}

inline void nyx_hal_spi_close(int64_t bus) {
    if (bus == 1) SPI1->CR1 &= ~(1UL << 6);
}

inline bool nyx_stm32f4_i2c_wait_sr1(uint32_t mask) {
    uint32_t timeout = NYX_STM32F4_IO_TIMEOUT;
    while (!(I2C1->SR1 & mask) && timeout > 0U) {
        if (I2C1->SR1 & 0x0F00UL) return false;
        --timeout;
    }
    return timeout != 0U;
}

inline bool nyx_stm32f4_i2c_wait_idle() {
    uint32_t timeout = NYX_STM32F4_IO_TIMEOUT;
    while ((I2C1->SR2 & (1UL << 1)) && timeout > 0U) --timeout;
    return timeout != 0U;
}

inline void nyx_stm32f4_i2c_clear_addr() {
    volatile uint32_t discard = I2C1->SR1;
    discard = I2C1->SR2;
    (void)discard;
}

inline bool nyx_stm32f4_i2c_start(uint8_t address, bool read) {
    I2C1->CR1 |= (1UL << 8);
    if (!nyx_stm32f4_i2c_wait_sr1(1UL << 0)) return false;
    I2C1->DR = ((uint32_t)address << 1U) | (read ? 1U : 0U);
    return nyx_stm32f4_i2c_wait_sr1(1UL << 1);
}

inline bool nyx_hal_i2c_init(int64_t bus, int64_t frequency) {
    if (bus != 1 || frequency <= 0 || frequency > 400000) return false;
    uint32_t ccr = 0;
    uint32_t trise = 0;
    uint32_t fast_mode = 0;
    if (frequency <= 100000) {
        ccr = NYX_STM32F4_CORE_CLOCK_HZ / ((uint32_t)frequency * 2U);
        if (ccr < 4U || ccr > 0x0FFFU) return false;
        trise = 17U;
    } else {
        ccr = NYX_STM32F4_CORE_CLOCK_HZ / ((uint32_t)frequency * 3U);
        if (ccr == 0U || ccr > 0x0FFFU) return false;
        trise = 6U;
        fast_mode = 1UL << 15;
    }
    RCC_AHB1ENR |= (1UL << 1);
    RCC_APB1ENR |= (1UL << 21);
    nyx_stm32f4_gpio_config_alt(24, 4, true); // PB8: I2C1 SCL
    nyx_stm32f4_gpio_config_alt(25, 4, true); // PB9: I2C1 SDA

    I2C1->CR1 = (1UL << 15);
    I2C1->CR1 = 0;
    I2C1->CR2 = 16U; // APB1 clock in MHz while running from reset HSI.
    I2C1->CCR = fast_mode | ccr;
    I2C1->TRISE = trise;
    I2C1->CR1 = (1UL << 10) | (1UL << 0); // ACK + peripheral enable.
    return true;
}

inline bool nyx_hal_i2c_probe(int64_t bus, int64_t address) {
    if (bus != 1 || address < 0 || address > 0x7F || !nyx_stm32f4_i2c_wait_idle()) return false;
    I2C1->SR1 &= ~0x0F00UL;
    if (!nyx_stm32f4_i2c_start((uint8_t)address, false)) {
        I2C1->CR1 |= (1UL << 9);
        I2C1->SR1 &= ~(1UL << 10);
        return false;
    }
    nyx_stm32f4_i2c_clear_addr();
    I2C1->CR1 |= (1UL << 9);
    return true;
}

inline int64_t nyx_hal_i2c_write_byte(int64_t bus, int64_t address, int64_t reg, int64_t value) {
    if (bus != 1 || address < 0 || address > 0x7F || !nyx_stm32f4_i2c_wait_idle()) return -1;
    I2C1->SR1 &= ~0x0F00UL;
    if (!nyx_stm32f4_i2c_start((uint8_t)address, false)) { I2C1->CR1 |= (1UL << 9); return -2; }
    nyx_stm32f4_i2c_clear_addr();
    if (!nyx_stm32f4_i2c_wait_sr1(1UL << 7)) { I2C1->CR1 |= (1UL << 9); return -3; }
    I2C1->DR = (uint8_t)reg;
    if (!nyx_stm32f4_i2c_wait_sr1(1UL << 7)) { I2C1->CR1 |= (1UL << 9); return -4; }
    I2C1->DR = (uint8_t)value;
    if (!nyx_stm32f4_i2c_wait_sr1(1UL << 2)) { I2C1->CR1 |= (1UL << 9); return -5; }
    I2C1->CR1 |= (1UL << 9);
    return 0;
}

inline int64_t nyx_hal_i2c_read_byte(int64_t bus, int64_t address, int64_t reg) {
    if (bus != 1 || address < 0 || address > 0x7F || !nyx_stm32f4_i2c_wait_idle()) return -1;
    I2C1->SR1 &= ~0x0F00UL;
    if (!nyx_stm32f4_i2c_start((uint8_t)address, false)) { I2C1->CR1 |= (1UL << 9); return -2; }
    nyx_stm32f4_i2c_clear_addr();
    if (!nyx_stm32f4_i2c_wait_sr1(1UL << 7)) { I2C1->CR1 |= (1UL << 9); return -3; }
    I2C1->DR = (uint8_t)reg;
    if (!nyx_stm32f4_i2c_wait_sr1(1UL << 2)) { I2C1->CR1 |= (1UL << 9); return -4; }
    if (!nyx_stm32f4_i2c_start((uint8_t)address, true)) { I2C1->CR1 |= (1UL << 9); return -5; }
    I2C1->CR1 &= ~(1UL << 10); // NACK the only byte.
    nyx_stm32f4_i2c_clear_addr();
    I2C1->CR1 |= (1UL << 9);
    if (!nyx_stm32f4_i2c_wait_sr1(1UL << 6)) { I2C1->CR1 |= (1UL << 10); return -6; }
    const uint8_t value = (uint8_t)I2C1->DR;
    I2C1->CR1 |= (1UL << 10);
    return (int64_t)value;
}

inline int64_t nyx_hal_i2c_write_buffer(
    int64_t bus, int64_t address, uintptr_t data, int64_t length
) {
    if (
        bus != 1 || address < 0 || address > 0x7F || length < 0 ||
        (length > 0 && data == 0U) || !nyx_stm32f4_i2c_wait_idle()
    ) return -1;
    const uint8_t* bytes = (const uint8_t*)data;
    I2C1->SR1 &= ~0x0F00UL;
    if (!nyx_stm32f4_i2c_start((uint8_t)address, false)) {
        I2C1->CR1 |= (1UL << 9);
        return -2;
    }
    nyx_stm32f4_i2c_clear_addr();
    for (int64_t index = 0; index < length; ++index) {
        if (!nyx_stm32f4_i2c_wait_sr1(1UL << 7)) {
            I2C1->CR1 |= (1UL << 9);
            return -3;
        }
        I2C1->DR = bytes[index];
    }
    if (length > 0 && !nyx_stm32f4_i2c_wait_sr1(1UL << 2)) {
        I2C1->CR1 |= (1UL << 9);
        return -4;
    }
    I2C1->CR1 |= (1UL << 9);
    return length;
}

inline int64_t nyx_hal_i2c_read_buffer(
    int64_t bus, int64_t address, uintptr_t data, int64_t length
) {
    if (
        bus != 1 || address < 0 || address > 0x7F || length < 0 ||
        (length > 0 && data == 0U) || !nyx_stm32f4_i2c_wait_idle()
    ) return -1;
    if (length == 0) return 0;
    uint8_t* bytes = (uint8_t*)data;
    I2C1->SR1 &= ~0x0F00UL;
    I2C1->CR1 |= (1UL << 10);
    if (!nyx_stm32f4_i2c_start((uint8_t)address, true)) {
        I2C1->CR1 |= (1UL << 9);
        return -2;
    }
    if (length == 1) I2C1->CR1 &= ~(1UL << 10);
    nyx_stm32f4_i2c_clear_addr();
    if (length == 1) I2C1->CR1 |= (1UL << 9);
    for (int64_t index = 0; index < length; ++index) {
        if (index == length - 1 && length > 1) {
            I2C1->CR1 &= ~(1UL << 10);
            I2C1->CR1 |= (1UL << 9);
        }
        if (!nyx_stm32f4_i2c_wait_sr1(1UL << 6)) {
            I2C1->CR1 |= (1UL << 10);
            I2C1->CR1 |= (1UL << 9);
            return -3;
        }
        bytes[index] = (uint8_t)I2C1->DR;
    }
    I2C1->CR1 |= (1UL << 10);
    return length;
}

inline int nyx_stm32f4_adc_channel(int64_t pin) {
    if (pin >= 0 && pin <= 7) return (int)pin;       // PA0..PA7
    if (pin == 16) return 8;                         // PB0
    if (pin == 17) return 9;                         // PB1
    if (pin >= 32 && pin <= 37) return (int)(pin - 22); // PC0..PC5
    return -1;
}

inline int64_t nyx_hal_adc_read(int64_t pin) {
    const int channel = nyx_stm32f4_adc_channel(pin);
    if (channel < 0 || !nyx_stm32f4_gpio_config_analog(pin)) return -1;
    RCC_APB2ENR |= (1UL << 8);
    ADC1->CR1 = 0;
    ADC1->CR2 = 1UL;
    ADC1->SQR1 = 0;
    ADC1->SQR3 = (uint32_t)channel;
    if (channel <= 9) {
        const uint32_t shift = (uint32_t)channel * 3U;
        ADC1->SMPR2 = (ADC1->SMPR2 & ~(7UL << shift)) | (4UL << shift);
    } else {
        const uint32_t shift = (uint32_t)(channel - 10) * 3U;
        ADC1->SMPR1 = (ADC1->SMPR1 & ~(7UL << shift)) | (4UL << shift);
    }
    for (uint32_t settle = 0; settle < 64U; ++settle) { __asm__ volatile("nop"); }
    ADC1->CR2 |= (1UL << 30);
    uint32_t timeout = NYX_STM32F4_IO_TIMEOUT;
    while (!(ADC1->SR & (1UL << 1)) && timeout > 0U) --timeout;
    return timeout == 0U ? -2 : (int64_t)(ADC1->DR & 0x0FFFUL);
}

inline STM32F4_TIM_TypeDef* nyx_stm32f4_timer(int64_t timer, uint32_t* clock_bit, int64_t* irq) {
#ifdef NYX_BOARD_NUCLEO_F410RB
    if (timer == 5) { *clock_bit = 3; *irq = 50; return TIM5; }
    if (timer == 6) { *clock_bit = 4; *irq = 54; return TIM6; }
#else
    if (timer == 2) { *clock_bit = 0; *irq = 28; return TIM2; }
    if (timer == 3) { *clock_bit = 1; *irq = 29; return TIM3; }
    if (timer == 4) { *clock_bit = 2; *irq = 30; return TIM4; }
#endif
    return nullptr;
}

inline bool nyx_stm32f4_timer_period(STM32F4_TIM_TypeDef* timer, int64_t frequency) {
    if (!timer || frequency <= 0 || frequency > (int64_t)NYX_STM32F4_CORE_CLOCK_HZ) return false;
    uint64_t ticks = (uint64_t)NYX_STM32F4_CORE_CLOCK_HZ / (uint64_t)frequency;
    if (ticks == 0U) ticks = 1U;
    uint32_t prescaler = (uint32_t)((ticks - 1U) / 65536U);
    if (prescaler > 0xFFFFU) return false;
    uint32_t period = (uint32_t)((uint64_t)NYX_STM32F4_CORE_CLOCK_HZ /
        ((uint64_t)(prescaler + 1U) * (uint64_t)frequency));
    if (period == 0U) period = 1U;
    if (period > 65536U) period = 65536U;
    timer->PSC = prescaler;
    timer->ARR = period - 1U;
    timer->EGR = 1U;
    timer->SR = 0;
    return true;
}

inline bool nyx_hal_timer_start(int64_t timer_number, int64_t frequency, bool with_interrupt) {
    uint32_t clock_bit = 0;
    int64_t irq = -1;
    STM32F4_TIM_TypeDef* timer = nyx_stm32f4_timer(timer_number, &clock_bit, &irq);
    if (!timer) return false;
    RCC_APB1ENR |= (1UL << clock_bit);
    timer->CR1 = 0;
    if (!nyx_stm32f4_timer_period(timer, frequency)) return false;
    timer->DIER = with_interrupt ? 1UL : 0UL;
    if (with_interrupt) {
        nyx_hal_irq_clear_pending(irq);
        nyx_hal_irq_enable(irq);
    }
    timer->CR1 = (1UL << 7) | 1UL;
    return true;
}

inline void nyx_hal_timer_stop(int64_t timer_number) {
    uint32_t clock_bit = 0;
    int64_t irq = -1;
    STM32F4_TIM_TypeDef* timer = nyx_stm32f4_timer(timer_number, &clock_bit, &irq);
    if (timer) timer->CR1 &= ~1UL;
}

inline void nyx_hal_timer_clear_update(int64_t timer_number) {
    uint32_t clock_bit = 0;
    int64_t irq = -1;
    STM32F4_TIM_TypeDef* timer = nyx_stm32f4_timer(timer_number, &clock_bit, &irq);
    if (timer) timer->SR &= ~1UL;
}

inline int64_t nyx_hal_timer_counter(int64_t timer_number) {
    uint32_t clock_bit = 0;
    int64_t irq = -1;
    STM32F4_TIM_TypeDef* timer = nyx_stm32f4_timer(timer_number, &clock_bit, &irq);
    return timer ? (int64_t)timer->CNT : -1;
}

inline int nyx_stm32f4_pwm_channel(int64_t pin) {
#ifdef NYX_BOARD_NUCLEO_F410RB
    (void)pin;
    return 0;
#else
    if (pin == 0 || pin == 5) return 1;  // PA0/PA5 TIM2_CH1
    if (pin == 1 || pin == 19) return 2; // PA1/PB3 TIM2_CH2
    if (pin == 2 || pin == 26) return 3; // PA2/PB10 TIM2_CH3
    if (pin == 3 || pin == 27) return 4; // PA3/PB11 TIM2_CH4
    return 0;
#endif
}

inline bool nyx_hal_pwm_init(int64_t pin, int64_t frequency) {
    const int channel = nyx_stm32f4_pwm_channel(pin);
    if (channel == 0 || !nyx_stm32f4_gpio_config_alt(pin, 1, false)) return false;
    RCC_APB1ENR |= (1UL << 0);
    TIM2->CR1 = 0;
    if (!nyx_stm32f4_timer_period(TIM2, frequency)) return false;
    if (channel == 1) {
        TIM2->CCMR1 = (TIM2->CCMR1 & ~0xFFUL) | (6UL << 4) | (1UL << 3);
        TIM2->CCR1 = 0;
        TIM2->CCER |= 1UL << 0;
    } else if (channel == 2) {
        TIM2->CCMR1 = (TIM2->CCMR1 & ~(0xFFUL << 8)) | (6UL << 12) | (1UL << 11);
        TIM2->CCR2 = 0;
        TIM2->CCER |= 1UL << 4;
    } else if (channel == 3) {
        TIM2->CCMR2 = (TIM2->CCMR2 & ~0xFFUL) | (6UL << 4) | (1UL << 3);
        TIM2->CCR3 = 0;
        TIM2->CCER |= 1UL << 8;
    } else {
        TIM2->CCMR2 = (TIM2->CCMR2 & ~(0xFFUL << 8)) | (6UL << 12) | (1UL << 11);
        TIM2->CCR4 = 0;
        TIM2->CCER |= 1UL << 12;
    }
    TIM2->EGR = 1UL;
    TIM2->CR1 = (1UL << 7) | 1UL;
    return true;
}

inline bool nyx_hal_pwm_write(int64_t pin, int64_t duty_per_mille) {
    const int channel = nyx_stm32f4_pwm_channel(pin);
    if (channel == 0) return false;
    if (duty_per_mille < 0) duty_per_mille = 0;
    if (duty_per_mille > 1000) duty_per_mille = 1000;
    const uint32_t compare = (uint32_t)(((uint64_t)(TIM2->ARR + 1U) *
        (uint64_t)duty_per_mille) / 1000U);
    if (channel == 1) TIM2->CCR1 = compare;
    else if (channel == 2) TIM2->CCR2 = compare;
    else if (channel == 3) TIM2->CCR3 = compare;
    else TIM2->CCR4 = compare;
    return true;
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
