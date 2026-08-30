#include <stddef.h>
#include <stdint.h>

// Minimal freestanding CRT surface required by official STM32 CMSIS startup
// files. Every symbol is weak so a configured libc/compiler runtime can
// replace it without duplicate-definition failures.
extern "C" {

using NyxInitFn = void (*)(void);

extern NyxInitFn __preinit_array_start[] __attribute__((weak));
extern NyxInitFn __preinit_array_end[] __attribute__((weak));
extern NyxInitFn __init_array_start[] __attribute__((weak));
extern NyxInitFn __init_array_end[] __attribute__((weak));
extern NyxInitFn __fini_array_start[] __attribute__((weak));
extern NyxInitFn __fini_array_end[] __attribute__((weak));

__attribute__((weak)) void __libc_init_array(void) {
    if (__preinit_array_start && __preinit_array_end) {
        for (NyxInitFn* fn = __preinit_array_start; fn < __preinit_array_end; ++fn) {
            if (*fn) (*fn)();
        }
    }
    if (__init_array_start && __init_array_end) {
        for (NyxInitFn* fn = __init_array_start; fn < __init_array_end; ++fn) {
            if (*fn) (*fn)();
        }
    }
}

__attribute__((weak)) void __libc_fini_array(void) {
    if (__fini_array_start && __fini_array_end) {
        for (NyxInitFn* fn = __fini_array_end; fn != __fini_array_start;) {
            --fn;
            if (*fn) (*fn)();
        }
    }
}

__attribute__((weak)) void* memcpy(void* destination, const void* source, size_t length) {
    auto* out = static_cast<uint8_t*>(destination);
    const auto* in = static_cast<const uint8_t*>(source);
    while (length--) *out++ = *in++;
    return destination;
}

__attribute__((weak)) void* memmove(void* destination, const void* source, size_t length) {
    auto* out = static_cast<uint8_t*>(destination);
    const auto* in = static_cast<const uint8_t*>(source);
    if (out < in) {
        while (length--) *out++ = *in++;
    } else if (out > in) {
        out += length;
        in += length;
        while (length--) *--out = *--in;
    }
    return destination;
}

__attribute__((weak)) void* memset(void* destination, int value, size_t length) {
    auto* out = static_cast<uint8_t*>(destination);
    while (length--) *out++ = static_cast<uint8_t>(value);
    return destination;
}

__attribute__((weak)) int memcmp(const void* left, const void* right, size_t length) {
    const auto* lhs = static_cast<const uint8_t*>(left);
    const auto* rhs = static_cast<const uint8_t*>(right);
    while (length--) {
        if (*lhs != *rhs) return *lhs < *rhs ? -1 : 1;
        ++lhs;
        ++rhs;
    }
    return 0;
}

__attribute__((weak)) void __aeabi_memcpy(void* destination, const void* source, size_t length) {
    memcpy(destination, source, length);
}

__attribute__((weak)) void __aeabi_memcpy4(void* destination, const void* source, size_t length) {
    memcpy(destination, source, length);
}

__attribute__((weak)) void __aeabi_memclr(void* destination, size_t length) {
    memset(destination, 0, length);
}

__attribute__((weak)) void __aeabi_memclr4(void* destination, size_t length) {
    memset(destination, 0, length);
}

__attribute__((weak)) int __cxa_atexit(void (*)(void*), void*, void*) { return 0; }
void* __dso_handle __attribute__((weak)) = nullptr;

[[noreturn]] __attribute__((weak)) void __cxa_pure_virtual(void) {
    while (true) __asm__ volatile("wfi");
}

[[noreturn]] __attribute__((weak)) void abort(void) {
    while (true) __asm__ volatile("wfi");
}

[[noreturn]] __attribute__((weak)) void _exit(int) {
    while (true) __asm__ volatile("wfi");
}

}  // extern "C"
