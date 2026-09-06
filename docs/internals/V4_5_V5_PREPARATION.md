# Nyx v4.5.0 ve v5.0.0 hazırlık kaydı

Güncelleme: 2026-09-06. İncelenen taban commit: `a49e413`; çalışma ağacı kirli.
`VERSION` ve `nyx.toml`: `4.0.0`. Bu kayıt yayın veya tamamlanmış v5 iddiası değildir.
İşlerin sırası takvime değil bağımlılıklara ve doğrulanabilir çıkış kapılarına bağlıdır.

Genel sürüm politikası [ROADMAP_AND_BACKEND_GATES.md](ROADMAP_AND_BACKEND_GATES.md),
değişiklik geçmişi [CHANGELOG.md](../../CHANGELOG.md), görev özeti
[TODO.md](../TODO.md) dosyasındadır. Bu dosya iki sürümün ayrıntılı lowering ve
geçiş planını, araştırma kararlarını ve bu çalışmanın doğrulama kaydını tutar.

## Mevcut kaynakta doğrulanan durum

| Bileşen | Kaynak | Gerçek durum |
|---|---|---|
| Typed HIR | `src/ir/model.py`, `types.py`, `serialization.py` | Immutable, ağaç biçimli HIR; schema v1, canonical JSON ve fingerprint var; SSA değildir |
| Lowering | `src/ir/lowering.py`, `compiler/hir_lowering.nyx` | Python ve Nyx frontend yolları var; değişikliklerin canonical byte parity kapısı var |
| Pass/verifier | `src/ir/passes.py`, `verifier.py` | Deterministik dönüşüm ve HIR doğrulaması mevcut |
| WASM | `src/codegen/wasm_ir.py` | HIR → ortak instruction graph → WAT ve binary; ayrı elle yazılmış iki codegen yolu kullanılmıyor |
| Native self-host | `compiler/`, `tests/self_host_suite.py` | Native compiler C++ üretir; C/LLVM self-host yolu henüz yok |
| Backend sicili | `src/core/backend_capabilities.py` | C++/JS/Python stable; Rust/WASM/React/ASM beta; `c` (C17 scalar) ve `llvm` (LLVM IR scalar) experimental kayıtlı |
| Benchmark | `src/toolchain/compiler_benchmark.py` | Python stage-0 ölçümü; native compiler hızlanması kanıtı değil |

WASM'ın `int` aritmetiği ve Array<int> elemanları mevcut uygulamada i32'dir.
Bu, stable C++/JS/Python signed-i64 semantiğine tam eşdeğer değildir; sicil WASM
için `int64_wrap` ilan etmiyor. v4.5 içinde ABI v1 genişliklerini sessizce
değiştirmek yerine bu sınır belgelenir. i64 iç temsil ve ABI v2 ayrı v5 kararıdır.

## Güncel uygulama changelog'u

### Oturum başında mevcut olan çalışmalar

- Array/string `len`, `length`, `size` dönüşleri HIR'da `int`; built-in
  `Result<T,E>` match payload'ları `T`/`E` olarak lower ediliyor.
- Python typechecker'da Result pattern binding türü ve kapsamı düzeltilmiş.
- LSP UTF-16 ve tanı alanları, kapanan belge ve bilinmeyen istek davranışı için
  düzeltmeler mevcut. References/rename/semantic tokens henüz tamamlanmış değil.
- Metrics örneği, docs bundle üretimi, preview worker ve stage-0 benchmark mevcut.
  Bunlar önceki yerel değişikliklerdir; bu oturumda sıfırdan yazılmış sayılmaz.

### Bu araştırmadan sonra düzeltilenler

1. **WASM sayısal dizi okuma lowering'i:** `IRIndexAccess` artık borrowed
   `Array<int>` ve `Array<float>` parametreleri için derlenir. Önceden bundle
   komutu `Unsupported expression 'IRIndexAccess'` ile duruyordu.
2. **Tek değerlendirme ve sınır kontrolü:** indeks helper parametresi olarak
   bir kez hesaplanır. Negatif indeks, boş dizi, `index >= length` ve geçersiz
   descriptor aralığı yükleme öncesi trap üretir. `ptr + length * stride`
   hesabı i64 ile yapılır; wasm32 adres taşmasıyla kontrol atlanmaz.
3. **Lazy Boolean lowering:** `and`/`or` ve eşdeğer operatörleri `if (result i32)`
   dallarına iner. Bitwise `i32.and/or` ile iki operandı çalıştırma hatası kapatıldı.
4. **Regresyonlar:** ilk/son eleman, negatif/boş/uzunluğa eşit indeks, i32/f64,
   nested erişim, yan etkili indeks, kısa devre, bozuk ham ABI descriptor'ı ve
   belleğin son geçerli elemanı yürütülür. String indeksleme ve diziye yazma
   desteklenmeyen yollar olarak reddedilir; başarısız bundle artifact bırakmaz.
5. **Üretilen örnekler:** lowering çıktısı değiştiği için Metrics/Pong bundle'ları
   mevcut `python -m src.toolchain.docs_site` komutuyla tekrar üretilir; hash
   manifesti eşlenir. Üretilmiş dosyalar elle düzenlenmez.
6. **Eski release-test beklentisi:** `7a76cb3` commit'i README footer'ını bilinçli
   kaldırmış, `tests/version_contract_suite.py` hâlâ zorunlu tutuyordu. Eski
   footer assertion'ı kaldırıldı; üç aktif diagram ve tüm sürüm eşleme kontrolleri
   korundu. README tasarımı değiştirilmedi.

Kod: `src/codegen/wasm_ir.py`. Testler: `tests/test_bundle.nyx`,
`tests/bundle_suite.py`. HIR şeması, ABI sürümü ve varsayılan hedef değişmedi.
Bu okuma desteği owned array, array assignment, string indexing veya tam WASM
runtime parity anlamına gelmez. Ham descriptor kontrolü linear-memory aralığını
doğrular; allocation sahipliğini kanıtlamaz. Trap, JavaScript'te
`WebAssembly.RuntimeError` olarak görülür; catch edilebilir Nyx exception desteği değildir.

## v4.5.0: sıralı ve uyumlu geliştirme

| ID | Öncelik / bağımlılık | Teslimat | Kapanma ölçütü / durum |
|---|---|---|---|
| 45-IR-1 | P0, ilk adım | Numeric array read ve lazy Boolean WASM lowering | Bu çalışmada uygulandı; bundle runtime regresyonu geçti |
| 45-IR-2 | P0, IR-1 sonrası | HIR node/type/span/capability envanteri | Uygulandı; string/Iterator indexing type loss giderildi, verifier generic ve primitive kuralı sıkılaştırıldı, Python/Nyx canonical byte parity korundu |
| 45-LSP | P1, sembol/span envanteri sonrası | Kaynak sembol indeksi, references → prepareRename/rename → semantic tokens | Uygulandı; LspSymbolIndex ile shadowing, UTF-16, function/struct scope, prepareRename/rename çakışma denetimi ve semanticTokens/full delta kodlama eklendi; lsp_suite 7/7 geçti |
| 45-PERF | P1, correctness yeşilken | Native frontend/codegen süre ve bellek baseline'ı | Uygulandı; src/toolchain/compiler_benchmark.py ve compiler_benchmark.json ile 4 kaynaklık sabit korpus üzerinde aşama bazlı süre/RSS/bellek baseline raporu (build/compiler-benchmark.json) üretildi |
| 45-LIB | P1 | Stdlib string/path/process API envanteri ve gerçek tüketici örnekleri | Her ek API'de hata/boş değer ayrımı, Result ve C++/JS/Python exact çıktı; açık |
| 45-WASM | P1, IR-1 sonrası | Ayrı capability işleri: assignment/ownership, string index, WASI args/env/files | Her iş için ABI kararı, pozitif/negatif runtime testleri; tamamlanmayan yetenek kapalı; açık |
| 45-RUST | P1 | Defer/Result/value-copy kapsamı, payload enum ve async/runtime boşlukları | Her açılan capability için rustc ile runtime parity; beta etiketi kanıtsız kalkmaz; açık |
| 45-PKG | P1 | Semver/registry/offline RFC ve deterministik resolver | Yerel lock ile remote resolution ayrılır; range/cycle/checksum/offline negatif corpus; açık |
| 45-V5 | P1 | Aşağıdaki C17/LLVM ve migration tasarımını prototipe dönüştür | C17 scalar pilotu tamamlandı (src/codegen/c17_scalar.py, tests/c17_scalar_suite.py, 'c' backend); LLVM IR ve migration araçları sonraki adım |
| 45-REL | Son, kapsamı dondurulmuş tüm işler sonrası | Release adayı ve platform kanıtı | Aynı revizyonda tam test, self-host, dört OS/arch işi, extension, checksum/SBOM ve paketleme; açık |

45-IR-2 sırasında öncelikli denetimler: string/member/index result türlerinin
gereksiz `any` olmaması, lexical symbol identity'nin emitter'da korunması,
destructuring/default-argument tek değerlendirmesi, erken dönüşte defer sırası,
pass öncesi/sonrası davranış, destek dışı HIR'ın output üretmeden reddi.
Bu başlıklar tamamlanmış hata düzeltmeleri olarak işaretlenmemelidir.

45-PERF için ölçüm notu: `tests/bootstrap_typechecker_test.py` native test
programını her semantik örnekte yeniden derliyor. Bu koşunun uzunluğu doğrudan
Nyx frontend latency ölçüsü değildir. Test hızlandırması ele alınırsa önce
harness derleme süresiyle örnek yürütme süresi ayrılır; tek harness reuse/cache
değişikliği aynı acceptance/rejection corpus'u koruyarak ayrıca ölçülür.

v4.5 RC'ye girişte yayın kapsamındaki P1 işleri açıkça seçilip dondurulur.
Yetişmeyen feature açıkça sonraki sürüme taşınır; kısmi implementation stable
diye yayınlanmaz. P0 correctness ve release kapıları ertelenmez.

## v5.0.0 Aether: lowering ve backend tasarım kaydı

Durum: **tasarım / uygulama bekliyor**. C17 veya LLVM emitter eklenmiş değildir.
v4 HIR'ı tamamen yeniden yazmak başlangıç koşulu değildir.

Önerilen sıra:

```text
v4.5 canonical HIR ve semantik fixture'ları
    -> C17 scalar pilotu
    -> LLVM scalar pilotu ve explicit control flow
    -> ortak lowering ihtiyacı ölçülür; gerekiyorsa dar bir internal LIR
    -> runtime, ownership, Result/defer, ABI ve platform conformance
    -> migration araçları + native bootstrap kanıtı
    -> v5 RC ve release kapısı
```

### 50-C: C17 experimental pilot

Durum: **C17 scalar pilotu uygulandı** (kod: `src/codegen/c17_scalar.py`, test: `tests/c17_scalar_suite.py`, backend: `c`). `clang -std=c17 -Wall -Wextra -Werror` ile C++ oracle parity doğrulandı.

- Girdi yalnız verified HIR; ilk kapsam `int`, `float`, `bool`, local,
  arithmetic/comparison, direct call, if/while ve return. String/Array/Struct,
  exception/Task, foreign binding desteği ayrıca uygulanana kadar reddedilir.
- Kaynak signed-i64 wrap semantiğini C signed overflow'una bırakma. Unsigned
  aritmetik ve tanımlı signed dönüş helper'ları kullan; division/remainder
  sıfır ve minimum-i64/-1 yollarını Nyx sözleşmesine göre dallandır.
- Üretilen C17'yi gerçek C toolchain ile derle; aynı fixture'ı C++/JS/Python
  oracle'larıyla karşılaştır. O0/O2 sonuçları aynı olmalı; platform/toolchain
  sürümü raporda tutulmalı. C17 kaynak üretimi tek başına native self-host değildir.
- Gate 1–7 geçmeden beta, sekiz kapı tamamlanmadan stable değerlendirmesi yok.

### 50-LLVM: direct LLVM IR experimental pilot

- İlk pilotun HIR kapsamı 50-C ile aynı; C++ ara kaynak adımı olmadan `.ll`
  üretimi ve gerçek LLVM doğrulama/derleme komutları gerekir. Kullanılacak LLVM
  sürümü pilot başında pinlenir; makinedeki Clang sürümü ürün sürüm taahhüdü değildir.
- Local değişkenleri ilk aşamada entry-block alloca/load/store ile temsil
  etmek mümkün; erken bir özel SSA sistemi zorunlu değil. Branch/terminator,
  type ve return doğruluğu LLVM verifier ile denetlenir. SSA dönüşümü ölçüm ve
  resmi pass pipeline üzerinden değerlendirilir.
- Nyx wrap aritmetiğinde kanıtsız `nsw/nuw` kullanılmaz. Division/remainder,
  shift-count sınırları ve lazy Boolean ifadeleri açık lowering ister.
- Float için varsayılan olarak fast-math yok; NaN, signed zero ve binary64
  fixture'ları korunur. Target triple/data layout hedef toolchain'den alınır;
  başka platformun pointer/alignment değerleri kopyalanmaz.
- HIR'da kaynak span/symbol identity tutulur; debug metadata sonraki ayrı
  teslimattır. Üretilmiş `.ll` dosyasının bulunması debugger desteği değildir.

### 50-LIR / 50-RUNTIME: ortaklaştırma sınırı

İkinci emitter aynı semantik dönüşümü tekrarlamaya başladığında ihtiyaç
kanıtlanırsa internal LIR eklenir. Başlangıçta bütün hosted emitter'ları bu
katmana geçirmek gerekmez. Public HIR JSON ile internal LIR formatı ayrıdır.

LIR kabul ölçütü: typed values, unique symbol/block kimlikleri, her block'ta
tek terminator, doğru branch hedefleri, single evaluation ve kaynak span
taşıma. Result `?`/return/break/continue için lexical defer cleanup yolları ve
Array/Struct copy/borrow kuralları ayrı fixture'larla doğrulanır. Exceptions,
Task/channel ve closure capture runtime tasarımı olmadan emüle edilmiş sayılmaz.

### 50-REF / 50-BOOT: bağımsız doğrulama ve native dağıtım

- OCaml reference frontend yalnız frozen grammar → canonical HIR/diagnostics
  doğrulayıcısıdır; yeni production compiler zorunluluğu değildir. Mevcut
  Python/Nyx parity corpus'u bağımsız parse ve diagnostic karşılaştırmasında kullanılır.
- Native `nyxc` için yeni backend erişimi ayrı iştir. Python tabanlı pilot
  emitter yazmak native compiler'ın C/LLVM desteklediği anlamına gelmez.
- Stage1 → Stage2 → Stage3 kanıtı, temiz kurulum ve paketleme testleri korunur.
  Default backend değişikliği için ayrı release kararı gerekir.

## Migration kapısı: hangi değişiklik hangi sürümü gerektirir?

| Yüzey | v4.5 kuralı | v5 için uygulanacak geçiş |
|---|---|---|
| Nyx kaynak semantiği | Geçerli v4 kodun anlamı korunur | Kırıcı öneri varsa önce/sonra örnekleri, tanı ve dönüşüm kılavuzu; otomatik sessiz reinterpretation yok |
| HIR JSON / plugin API | Schema v1 ve canonical parity korunur | Alan kaldırma/anlam değiştirme HIR v2; okuyucu sürümü doğrular, v1 geçiş fixture'ları gerekir |
| Internal LIR | Henüz yok; public HIR yerine geçirilmez | Gerekirse ayrı internal sürüm/fingerprint; plugin sözleşmesine kendiliğinden eklenmez |
| WASM Bundle ABI | v1 i32/UTF-8 ptr-len/borrow sözleşmesi korunur | i64 genişliği, owned array/struct dönüşü gibi değişiklikler ABI v2 ve loader/types migration gerektirir |
| Host importları | `nyx_host_v1` korunur | Signature/lifetime değişikliği yeni namespace; yanlış host sürümü reddedilir |
| Package lock | Mevcut local lock davranışı korunur | Registry kimliği, range çözümü ve zorunlu alanlar için format kararı ve deterministik migration; bilinmeyen format reddedilir |

Her v5 kırıcı değişiklik için örnek kaynak + eski/yeni artifact + kullanıcı
etkisi + dönüştürme yolu + negatif test kaydı gerekir. Bir sürüm numarası
değiştirmek migration değildir. v5 yayın şartı seçilmiş kapsamın sekiz backend
kapısını karşılamasıdır; C/LLVM'nin ikisini de stable ilan etmek zorunlu hedef değildir.
Go/JVM/.NET/Lua bu hazırlık çalışmasının teslimatı değildir.

## Araştırma kaynakları ve Nyx'e etkisi

2026-09-06 tarihinde resmi kaynaklarla kontrol edildi. Aşağıdaki uygulama
kararları Nyx tasarım önerisidir; standardın Nyx'e otomatik dayattığı kurallar değildir.

- [WebAssembly instruction semantics](https://webassembly.github.io/spec/core/exec/instructions.html):
  `unreachable` trap üretir; `if` yalnız seçilen dalı yürütür. Load'un linear-memory
  sınırı Nyx dizi uzunluğunu bilmez. Bu nedenle logical bounds ve widened
  descriptor kontrolü yüklemeden önce yapılır. Yeni bir WASM 3.0 feature bağımlılığı eklenmedi.
- [LLVM add semantics](https://llvm.org/docs/LangRef.html#add-instruction) ve
  [sdiv semantics](https://llvm.org/docs/LangRef.html#sdiv-instruction): wrap ile
  `nsw/nuw` poison farklıdır; zero/overflow division guard ister. Shift ve
  target-layout kuralları aynı Language Reference üzerinden pilotta uygulanır.
- [LLVM UB manual](https://llvm.org/docs/UndefinedBehavior.html): poison/UB
  optimizasyon altında davranışı değiştirebilir; output'un parse olması yeterli test değildir.
- [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf),
  §6.2.5, §6.5, §6.5.7: unsigned modulo, signed overflow ve shift kurallarının
  açık erişimli C11 metni. Bu dosya C17 final standardı diye sunulmaz;
  [WG14 sürüm listesi](https://open-std.org/jtc1/sc22/wg14/www/projects.html)
  C17'yi ISO/IEC 9899:2018 olarak listeler. C17 pilotu gerçek C17 modunda doğrulanır.

## Bu revizyonun doğrulama kaydı

- TESTED: `python tests/c17_scalar_suite.py`; C17 experimental scalar pilotu `clang -std=c17 -Wall -Wextra -Werror` altında sıfır uyarı/hata ile derlendi ve yürütüldü. 64-bit integer wrapping, güvenli sıfıra bölme / `INT64_MIN / -1` abort/wrap, scalar kontrol akışı ve özyineleme (`fib`), C++ oracle çıktısıyla birebir eşlendi; skalar olmayan veri yapıları (`Array`, `Struct`) derleme zamanında reddedildi.
- TESTED: `python tests/ir_suite.py`; 162 program, 18 stdlib modülü, 196-case Nyx/Python canonical HIR byte parity, string indexing ve negatif `IRVerifier` testleri (primitif member erişimi `HIR0006`, struct generic/optional alan doğrulaması, array/string indeks türü) geçti.
- TESTED: `python tests/bundle_suite.py`; düzeltme öncesi yeni fixture
  `IRIndexAccess` hatasını yeniden üretti, düzeltme sonrası geçti. 100.000
  allocation stress, yeni bounds/short-circuit ve negatif compile senaryoları dahil.
- TESTED: `python -m src.toolchain.docs_site`; Metrics/Pong yeniden üretildi.
- Tam batarya ilk koşuda yeni lowering ile eski `docs/generated/metrics/metrics.wasm`
  arasındaki byte farkını yakaladı. Artifactlar kaynak komutuyla yenilendi;
  sonraki koşuda docs-site doğrulaması geçti.
- TESTED: birleşik bataryada self-host reproducibility, 197-case Python/Nyx
  canonical HIR parity, 162-program corpus, C++/JS/Python runtime ve Rust
  metadata/runtime kapıları, language/numeric/Maya surface ve deterministik
  ZIP/TAR paketleme geçti.
- İkinci birleşik koşu, önceden var olan README footer assertion'ında durdu.
  Commit geçmişinden kaldırmanın kasıtlı olduğu doğrulanıp test düzeltildi.
  `run_version_contract_suite` geçti; bataryanın bu noktadan sonraki 23 suite'i
  aynı runner fonksiyonlarıyla ayrıca yürütüldü ve 23/23 `True`, process exit 0
  döndü. Böylece runner'ın bütün bileşenleri iki bölümde doğrulandı; tek
  kesintisiz full-suite başarısı olarak raporlanmaz. Son eklenen bundle negatif
  testleri ayrıca `python tests/bundle_suite.py` ile geçti.
- TESTED: kalan grupta installer, module/LSP/smoke, 530 fuzz vakası (0 unhandled
  crash), differential ve JS/Rust/C++ e2e, FFI/library/manifest/link/platform/SDK/
  interop, bootstrap lexer/parser/typechecker ve 138/138 regresyon geçti.
- TESTED: `npm --prefix vscode-extension test` geçti.
- VALIDATED: değişikliklerin `git diff --check` kontrolü ve altı plan/changelog
  belgesindeki yerel Markdown bağlantıları geçti.
- Ortam: Windows, Python 3.12.10, Node.js 24.19.0, Clang 22.1.8.
- NOT TESTED: Linux/macOS CI, bağımsız WAT assembler, platform-native dağıtım
  paketlerinin temiz makine/yayın doğrulaması ve v5 C17/LLVM runtime; bu pilotlar
  henüz uygulanmadı. Bu çalışma commit/tag/push/yayın yapmaz.

Sonraki revizyonda tek komutla tekrar kontrol: `python -u tests/run_all_tests.py`.
WASM codegen değişirse önce `python -m src.toolchain.docs_site` ile site
artifactlarını eşle, ardından bundle/docs-site ve tam batarya kontrollerini çalıştır.

## Sonraki oturumun başlangıç noktası

1. `git status --short` ile bu kayıttan sonraki değişiklikleri kontrol et.
2. Bu dosyanın doğrulama kaydı ve 45-IR-2 envanterinden devam et; bitmiş array
   read/lazy Boolean işini tekrar tasarlama.
3. Yeni lowering tür bilgisini değiştiriyorsa Python ve Nyx lowerer'ları birlikte
   güncelle; HIR byte parity ve self-host koşusunu tamamla.
4. Yeni işi ID'siyle bu dosyaya ve `CHANGELOG.md` Unreleased bölümüne işle;
   TESTED/REVIEWED/NOT TESTED ayrımını, komutu ve varsa açık hata kaydını koru.
