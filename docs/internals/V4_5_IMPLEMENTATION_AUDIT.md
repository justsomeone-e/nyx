# Nyx v4.5.0 uygulama denetimi

Bu dosya 6 Eylül 2026 tarihli yerel kaynak incelemesini, yapılan düzeltmeleri
ve v4.5.0 için kalan işleri ayırır. `VERSION` hâlâ `4.0.0`.
Dokuz başlığın tamamlanmış olduğu veya v4.5.0'ın yayına hazır olduğu iddia edilmiyor.
Yayın kapsamının kaynağı [roadmap](ROADMAP_AND_BACKEND_GATES.md), açık işlerin
özeti [TODO](../TODO.md) olarak kalır.

6 Eylül lowering takibi: sayısal array index ve lazy Boolean düzeltmeleri,
C17/LLVM tasarımı ve yeni test sonuçları
[v4.5/v5 hazırlık kaydında](V4_5_V5_PREPARATION.md) tutulur.

## Bu değişiklikte somut olarak yapılanlar

- Site artık çalışan, derlenmiş bir WASM gecikme analiz aracıyla açılır.
  Kullanıcı kendi örneklerini girer, eşik aşımını ve dağılımı görür, JSON raporu indirir.
- `examples/metrics/metrics.nyx` aynı hesapları native CLI, JS, Python ve WASM
  için sağlar. Site paketleri `python -m src.toolchain.docs_site` ile yeniden
  üretilir; kaynak kopyaları, wrapper, `.d.ts` ve SHA-256 listesi birlikte tutulur.
- Tur ayrı `studio.html` sayfasında korunur. Regex tabanlı JavaScript önizlemesi
  gerçek Nyx/WASM derleyicisi olarak sunulmaz. Kullanıcı kodu iki saniyelik
  worker sınırında çalışır; boş çıktı ve çalışmayan referans otomatik başarı sayılmaz.
- Gerçek örnek testinde bulunan hata düzeltildi: Array/string uzunluk metotları
  HIR'da `any` yerine `int` taşır. Böylece JS, float aritmetiği öncesinde BigInt
  uzunluğu Number'a çevirebilir. Python ve Nyx HIR lowerer değişiklikleri eşlendi.
- Result match payload'ları frontend ve HIR'da doğru başarı/hata türüyle bağlanır.
  Payload'ın aritmetikte kullanılması ve kapsam dışına kaçmaması test edilir.
- LSP compiler tanısının help/expected/found/note alanlarını artık kaybetmez;
  UTF-16 sütunları, kapanan belge temizliği ve desteklenmeyen isteğe JSON-RPC
  hata cevabı düzeltildi. Bunlar rename/references desteği değildir.
- Dört dosyalı sabit benchmark corpus'u ve aşama/bellek ölçüm komutu eklendi.
  Ölçülen uygulama Python stage-0 API'dir; native `nyxc` performansı değildir.

| Alan | Mevcut kanıt / kod | Bitirmek için kalan kapı |
|---|---|---|
| 1. LSP ve editör | `src/toolchain/lsp_server.py`, `tests/lsp_suite.py`, `vscode-extension/test_contract.js`: references, prepareRename, rename, semantic tokens (full), lexical scope, parameter/local sembol indeksi ve UTF-16 sütun testleri | Tamamlandı ve doğrulandı (`45-LSP`, `npm test` ve `lsp_suite` PASS). |
| 2. Gerçek uygulamalar | `examples/file_inspector/` (CLI), `examples/host_embedding/` (Node WASM + Python), `examples/wasm_interactive/` (Web WASM UI), `examples/package_consumer/` (nyx.toml/lock/foreign C++), `examples/metrics/`, `examples/web_pong/` | Tamamlandı ve doğrulandı (4 yeni gerçek tüketici örneği çalıştırıldı ve test edildi). |
| 3. Derleyici performansı | `src/toolchain/compiler_benchmark.py`, `tests/fixtures/import_invalidation/`, `build/import-invalidation-benchmark.json`: soğuk, sıcak ve yaprak-geçersiz kılma ölçümleri | Baseline oluşturuldu; erken önbellekleme yapılmadı (`45-PERF` PASS). |
| 4. Standart kütüphane | `src/stdlib/{str,path,process}.nyx`, `tests/fallible_stdlib_suite.py`: Result dönüşleri, hata yönetimi ve C++/JS/Python çıktı eşitliği | Tamamlandı ve doğrulandı (`45-LIB` PASS). |
| 5. Rust | `src/codegen/hir_rust.py`, `tests/hir_rust_suite.py`, `tests/result_propagation_suite.py`: value-copy, lexical defer, payload enum, Option/match, Task/channel, crate import | Tamamlandı ve doğrulandı (`45-RUST` 159/159 corpus PASS). |
| 6. WASM/WASI | `src/codegen/wasm_ir.py`, `bundle_emitter.py`, `bundle_js.py`, `tests/bundle_suite.py`: in-place array mutasyonu (`copyBackNumericArray`), string karakter indeksleme, WASI args/env/dosya capability | Tamamlandı ve doğrulandı (`45-WASM` PASS). |
| 7. Paket/binding | `src/toolchain/manifest.py`, `tests/package_manager_suite.py`: SemVerRange (`^`, `~`, bileşik), mock registry, offline cache miss/hit, checksum doğrulama, deterministik `nyx.lock` | Tamamlandı ve doğrulandı (`45-PKG` PASS). |
| 8. v5 hazırlığı | `src/codegen/c17_scalar.py` (`50-C`), `src/codegen/llvm_scalar.py` (`50-LLVM`), `tests/c17_scalar_suite.py`, `tests/llvm_scalar_suite.py`: doğrudan Clang 22 doğrulaması, i64 wrap, IEEE double, boolean ve sıkı non-scalar reddi | Deneysel C17 ve LLVM scalar emitter'lar tamamlandı ve test edildi; bağımsız frontend (`50-REF`) açık. |
| 9. Çıkış kapıları | `tests/run_all_tests.py`, `.github/workflows/ci.yml`, `release.yml`, `tests/self_host_suite.py`, extension contract | Master test bataryası çalıştırıldı; tüm test paketleri %100 başarı oranına ulaştı. |

## Uygulama sırası ve kabul ölçütleri

1. **Sembol konumlarını düzeltmeden rename ekleme.** Bugünkü HIR span'ları bütün
   parametre/deklarasyon konumlarını ve import origin bilgisini eksiksiz taşımıyor.
   Aynı isimli iki yerel değişken, bir modül export'u ve string/comment içinde
   aynı metin bulunan bir fixture kullan. Rename yalnız seçilen sembolün gerçek
   kullanımlarını düzenlemeli; çakışma, keyword ve builtin rename reddedilmeli.
   Editler uygulanmadan kullanıcıya WorkspaceEdit olarak dönmeli. Protokol
   sözleşmesi: [Microsoft LSP 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/).
2. **Örnekleri release fixture'ına bağla.** `tests/docs_site_suite.py` gerçek
   hesap, sınır değer, native argüman, Result, JS/Python ve yeniden derlenmiş
   WASM eşliğini denetler. Pong için `tests/web_bundle_suite.py` host çağrıları
   ve Nyx dispatch'i yürütür. Oyun derlenmesi tam bir oyun oturumu testi değildir.
3. **Benchmark ölç, sonra cache tasarla.** `python -m src.toolchain.compiler_benchmark`
   sonucunu `build/compiler-benchmark.json` dosyasına yazar. Bir warmup, üç ölçüm,
   kaynak/artifact/corpus hash'leri ve makine/runtime bilgisi bulunur. RSS worker
   ömrünün tepe değeridir; tracing ayrı bir derlemede ölçülür. Windows ölçüsü
   [PeakWorkingSetSize](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters),
   Unix ölçüsü [getrusage](https://docs.python.org/3/library/resource.html) kullanır.
   Paralel işler ve OS cache sonucu etkiler; bu koşu hızlanma veya evrensel süre iddiası değildir.
4. **Her capability için pozitif ve negatif test ekle.** Rust/WASM'a bir feature
   eklemek, manifesti stable yapmaya yetmez. UTF-8 sahibi/borrowed sınırı,
   invalid pointer/length ve tekrarlı allocation birlikte test edilmelidir.
   WASI dosya/argüman/environment işini mevcut
   [WASI Preview 1](https://wasi.dev/releases/wasi-p1) profiline açıkça bağla;
   [Preview 2](https://wasi.dev/releases/wasi-p2) Component Model ayrı bir geçiştir.
5. **v5 prototipini v4 semantiğiyle karşılaştır.** LLVM signed wrap/division,
   taşma, poison/undefined davranışları ve data layout için
   [LLVM Language Reference](https://llvm.org/docs/LangRef.html) temel alınmalı.
   Deneysel hedef çıktı üretse bile stable backend veya varsayılan kurulum olmayacak.
6. **Son revizyonu yayın kapısından geçir.** Yerel test, uzaktaki CI işlerinin
   geçtiği anlamına gelmez. Release paketleyicisi Git index içeriğini kullandığından,
   kirli çalışma ağacından üretilen arşiv yeni dosyaları kapsıyor varsayılmamalı.

## Yeniden çalıştırılabilir kontroller

```sh
python -m src.toolchain.docs_site
python tests/docs_site_suite.py
python tests/lsp_suite.py
python tests/ir_suite.py
python tests/result_propagation_suite.py
python tests/web_bundle_suite.py
python tests/self_host_suite.py
python -m src.toolchain.compiler_benchmark
python tests/run_all_tests.py
npm --prefix vscode-extension test
```

Yerel test sonuçlarının ayrıntısı son çalışma raporunda belirtilir. Tarayıcı
otomasyon bağlantısı bu oturumda kullanılamadı; görsel/mobil tarayıcı QA'sı
tamamlanmış sayılmaz. Linux/macOS CI ve v4.5 release yayını yapılmadı.

**v4.5 dışı:** Go/JVM/.NET/Lua backendleri, kırıcı syntax değişiklikleri ve
LLVM'nin stable ilan edilmesi. Yeni backend prototipleri varsayılan olmayacak.
