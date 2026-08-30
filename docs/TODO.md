# Nyx v4 TODO

## Tamamlandı

- [x] v3.0.0-beta.4 yayını.
- [x] C++20, ES2022, Python 3, Rust 2021, React 19, WASM ve gömülü hedefler.
- [x] Bundle ABI v1 ve React hook paketi.
- [x] Çoklu hedef stdlib sözleşmesi ve parity testleri.
- [x] Typed HIR v1, doğrulayıcı, deterministik serileştirme ve optimizasyon geçişleri.
- [x] HIR tabanlı WASM üretimi ve runtime-equivalence testleri.
- [x] Public compiler API, plugin sözleşmesi, LSP ve taşınabilir kurucular.
- [x] 138/138 regresyon ve birleşik test bataryası.
- [x] `hecpp` üreticisini AST'den HIR'a taşı.
- [x] `hejs` üreticisini AST'den HIR'a taşı.
- [x] `hepy` referans üreticisini AST'den HIR'a taşı.
- [x] `hers` Rust 2021 üreticisini AST'den canonical typed HIR'a taşı ve 159 kabul + 3 açık capability-rejection corpusunda `rustc` ile doğrula.
- [x] `let`/`const`, `Task<T>`, exception, trait ve strict-`bool` sözleşmelerini dondur.
- [x] i64, binary64, bölme, taşma, shift ve canonical scalar-text semantiğini dondur.
- [x] Native stage-1 derleyiciyi tam kabul/ret corpusunda doğrula.
- [x] Native `nyxc input.nyx output.cpp` stage-2 frontend'ini üret ve çalıştır.
- [x] Stage-2'nin aynı compiler kaynağından byte-identical stage-3 C++ üretmesini doğrula.
- [x] Nyx-authored AST -> typed HIR lowering katmanını tamamla.
- [x] Normal `nyxc check/emit-cpp/compile` ve kurulum yolundan Python zorunluluğunu kaldır.
- [x] Windows, Linux ve macOS CI matrisini tanımla.
- [x] VS Code için yerel VSIX, tek-tık Run/Build/Check ve kalıcı terminal komutlarını paketle.
- [x] `hecpp` için Clang++/GCC/G++/MSVC ve `NYX_CXX` teşhislerini CLI ile editörde eşitle.
- [x] `fmt/lint/debug/profile/doc/add/remove/install/pkg` komutlarını gerçek dosya/process etkisi, dürüst çıktı ve hata exit-code sözleşmesiyle doğrula.
- [x] `volatile`, `interrupt fn`, `critical` ve sabit genişlikli embedded tiplerini Python/Nyx lexer-parser eşliğiyle ekle.
- [x] Nucleo kart profili, connector alias, gerçek F4 GPIO/UART/SPI/I²C/ADC/PWM/timer/NVIC HAL ve ELF vektör doğrulamasını ekle.
- [x] Fiziksel HAL modüllerindeki masaüstü sahte başarı/stub davranışını kaldır.
- [x] Freestanding `Buffer<T, N>` ve allocation-free SPI/I²C/UART toplu aktarım ABI'sini ekle.

## v4.0.0-rc.1 kalanlar

- [x] `any` koşullarında runtime `bool` doğrulamasıyla implicit truthiness'i tamamen kapat.
- [ ] Temiz Windows/Linux/macOS x64 ve macOS arm64 paketleme-soak matrisini çalıştır.
- [x] Makineye özel yol ve timestamp bırakmadan yeniden üretilebilir release arşivi oluştur.
- [x] Kaynak arşivleri, native binaryler ve VSIX için checksum, provenance ve SPDX SBOM iş akışını tanımla ve sözleşmesini doğrula.
- [x] README, changelog, spec, manifest, CLI ve VS Code geliştirme sürümlerini `VERSION` kaynağıyla eşitle.
- [ ] Temiz çapraz-platform kapısından sonra tüm yüzeyleri ve etiketi tam `4.0.0-rc.1` sürümüne geçir.
- [ ] `v4.0.0-rc.1` release auditini temiz checkout'ta iki kez geçir.

## v4.0.0 stable

- [x] Stage 1'in stage 2'yi üretmesini sağla.
- [x] İki stage-2 derlemesinde eş HIR/çıktı kanıtla.
- [ ] Stable backendlerin tamamını sekiz kalite kapısından geçir.
- [ ] HIR, compiler API, plugin API ve Bundle ABI uyumluluk politikasını yayınla.
- [ ] Checksum, provenance/SBOM ve geri dönüş prosedürünü yayınla.
- [ ] RC soak süresini blockersız tamamla ve `v4.0.0` yayın kararını ver.

## RC1 sonrası yeni hedefler

- [ ] DMA stream, EXTI, input-capture/encoder ve watchdog typed API'leri.
- [ ] Kayıtlı Nucleo profilleri için STM32Cube/CMSIS provider ve gerçek kart üzerinde HIL matrisi.

- [ ] `hec` — C17.
- [ ] `hellvm` — doğrudan LLVM IR.
- [ ] `hego` — Go.
- [ ] `hejvm` — JVM/Java 21 uyumlu class dosyaları.
- [ ] `hedotnet` — .NET 10.
- [ ] `helua` — Lua 5.4.
- [ ] `nyx-ocaml` — bağımsız parser/typechecker ve canonical HIR oracle.
