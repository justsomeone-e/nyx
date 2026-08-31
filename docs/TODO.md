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
- [x] `cpp` üreticisini AST'den HIR'a taşı.
- [x] `js` üreticisini AST'den HIR'a taşı.
- [x] `python` referans üreticisini AST'den HIR'a taşı.
- [x] `rust` Rust 2021 üreticisini AST'den canonical typed HIR'a taşı ve 159 kabul + 3 açık capability-rejection corpusunda `rustc` ile doğrula.
- [x] `let`/`const`, `Task<T>`, exception, trait ve strict-`bool` sözleşmelerini dondur.
- [x] i64, binary64, bölme, taşma, shift ve canonical scalar-text semantiğini dondur.
- [x] Native stage-1 derleyiciyi tam kabul/ret corpusunda doğrula.
- [x] Native `nyxc input.nyx output.cpp` stage-2 frontend'ini üret ve çalıştır.
- [x] Stage-2'nin aynı compiler kaynağından byte-identical stage-3 C++ üretmesini doğrula.
- [x] Nyx-authored AST -> typed HIR lowering katmanını tamamla.
- [x] Normal `nyxc check/emit-cpp/compile` ve kurulum yolundan Python zorunluluğunu kaldır.
- [x] Windows, Linux ve macOS CI matrisini tanımla.
- [x] VS Code için yerel VSIX, tek-tık Run/Build/Check ve kalıcı terminal komutlarını paketle.
- [x] `cpp` için Clang++/GCC/G++/MSVC ve `NYX_CXX` teşhislerini CLI ile editörde eşitle.
- [x] `fmt/lint/debug/profile/doc/add/remove/install/pkg` komutlarını gerçek dosya/process etkisi, dürüst çıktı ve hata exit-code sözleşmesiyle doğrula.
- [x] `volatile`, `interrupt fn`, `critical` ve sabit genişlikli embedded tiplerini Python/Nyx lexer-parser eşliğiyle ekle.
- [x] Nucleo kart profili, connector alias, gerçek F4 GPIO/UART/SPI/I²C/ADC/PWM/timer/NVIC HAL ve ELF vektör doğrulamasını ekle.
- [x] Fiziksel HAL modüllerindeki masaüstü sahte başarı/stub davranışını kaldır.
- [x] Freestanding `Buffer<T, N>` ve allocation-free SPI/I²C/UART toplu aktarım ABI'sini ekle.
- [x] Resmî STM32Cube sparse installer/provider, karma C/C++/ASM derleme ve 25 kartlık ELF/HEX/BIN matrisini ekle.
- [x] Maya expression-bodied `fn`, değer üreten `if` ve exhaustive literal `match` sözdizimini Python/Nyx AST, typechecker ve HIR parity ile ekle.

## v4.0.0-rc.1 kalanlar

- [x] Pre-Nyx uyumluluk yüzeyini ve eski target adlarını kaldır; kanonik `cpp/js/python/rust/wasm/react/asm` göçünü hedefli regresyonda doğrula.
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

- [ ] Value-match için `Ok(value)` / `Err(error)` ve enum destructuring.
- [ ] `Result<T, E>` için type-safe `?` hata yayılımı.
- [ ] Array/struct destructuring declarations ve slice patterns.
- [ ] Tail-expression block'ları ve iterator/yield protokolü.
- [ ] Compile-time `when` ile hedef/capability seçimi.

- [ ] DMA stream, EXTI, input-capture/encoder ve watchdog typed API'leri.
- [ ] Kayıtlı Nucleo profilleri için gerçek kart üzerinde GPIO/UART/SPI/I²C HIL matrisi.

- [ ] `c` — C17.
- [ ] `llvm` — doğrudan LLVM IR.
- [ ] `go` — Go.
- [ ] `jvm` — JVM/Java 21 uyumlu class dosyaları.
- [ ] `dotnet` — .NET 10.
- [ ] `lua` — Lua 5.4.
- [ ] `nyx-ocaml` — bağımsız parser/typechecker ve canonical HIR oracle.
