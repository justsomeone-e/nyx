<div align="center">

# ⚡ HolyEasyLang

### One Syntax. Multiple Backends. One Language.

**A polyglot programming language designed to write once and target multiple ecosystems.**

<br/>

[![Version](https://img.shields.io/badge/version-v4.0.0--beta.1-8A2BE2?style=for-the-badge)](https://github.com/)
[![C++20](https://img.shields.io/badge/C++20-stable-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)](https://isocpp.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-stable-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![Python](https://img.shields.io/badge/Python-reference-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Rust](https://img.shields.io/badge/Rust-active%20conformance-000000?style=for-the-badge&logo=rust&logoColor=white)](https://rust-lang.org/)
[![License](https://img.shields.io/badge/license-MIT-00A98F?style=for-the-badge)](LICENSE)

<br/>

**Write it once. Target the ecosystem you need.**

</div>

---

## ✦ What is HolyEasyLang?

HolyEasyLang is a multi-target programming language with a single language core and multiple code-generation backends.

Instead of learning a completely different syntax for every target:

```text
                    HolyEasyLang
                         │
                  Lexer → Parser
                         │
                    Type Checker
                         │
                    Typed AST
                         │
        ┌────────────────┼────────────────┐
        │                │                │
      hecpp             hejs             hepy
        │                │                │
      C++20          JavaScript         Python
        │                │                │
        └────────────────┼────────────────┘
                         │
                       hers
                         │
                       Rust
