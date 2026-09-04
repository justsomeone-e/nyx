# Nyx v4 Development TODO

Bu dosya Nyx v4 geliştirme hattının aktif görev listesidir. `v4.0.0-rc.1
Samsara` yayınlandı; aktif aday `v4.0.0-rc.2 Bodhi`, stable hedef ise
`v4.0.0 Nirvana`dır.

## Yön kararları

- [x] STM32, Nucleo, RP2040, AVR ve genel freestanding firmware hedeflerini v4
  geliştirme kapsamından çıkar.
- [x] Board profilleri, firmware flasher, STM32Cube sağlayıcısı ve fiziksel HAL
  modüllerini aktif compiler/tooling yüzeyinden kaldır.
- [x] Embedded'e özel `volatile`, `interrupt`, `critical`, `Buffer<T, N>` ve
  `buffer_ptr` kalıntılarını iki frontend, HIR, codegen, LSP ve editörden kaldır;
  kullanılmayan keyword bırakma.
- [ ] Sabit boyutlu koleksiyon gerekiyorsa bunu donanım hedefinden bağımsız yeni
  bir `Array<T, N>`/`array[T, N]` RFC'si olarak tasarla.
- [x] Ana hedefleri `cpp`, `js`, `python`, `rust`, `wasm`, `react` ve `asm`
  olarak sınırla.
- [x] Birincil geliştirme hedeflerini `cpp` native ve `wasm` olarak belirle;
  diğer backendleri açık capability sözleşmeleriyle koru.

## Compiler çekirdeği

- [x] `nyx build/run` için host-native varsayılanını tamamla; kaynak dosyada
  `#target` zorunluluğunu kaldır ve CLI/manifest override sırasını dondur.
- [x] Python ve Nyx frontendlerinin lexer, parser, typechecker ve canonical HIR
  parity kapısını her syntax değişikliğinde zorunlu tut.
- [ ] HIR verifier hata kodlarını ve source-span davranışını public sözleşme yap.
- [ ] C++ emitter'ın yalnız kullanılan runtime parçalarını üretmesini sağla;
  gereksiz include ve boilerplate maliyetini ölç.
- [x] Stage 1 -> Stage 2 -> Stage 3 self-host zincirini temiz checkout'ta iki
  kez doğrula ve Python sınırını açıkça belgeleyip test et.
- [ ] Modül grafiği, cycle diagnostics ve incremental cache anahtarlarını
  deterministik hale getir.
- [ ] Compiler crash'lerini structured diagnostic'e dönüştüren negatif corpusu
  genişlet.

## Kullanılabilir syntax — Nim/Haxe esintili, Nyx semantiği

Yeni keyword yalnız yeni ve test edilebilir bir semantik getiriyorsa eklenir.
Alias veya completion listesini şişiren eş anlamlı keyword eklenmez. Her madde
Python parser + Nyx parser + typechecker + HIR + backend parity gerektirir.

- [x] Expression-bodied function: `fn square(x: int) -> int = x * x`.
- [x] Değer üreten exhaustive `if` ve literal `match` ifadeleri.
- [x] Payload enum: `enum Result<T, E> { Ok(T), Err(E) }` (`cpp`, `js`,
  `python`; diğer hedeflerde açık capability hatası).
- [x] Variant constructor ve enum destructuring pattern'ları:
  `Success(value)`, `Point(x, y)` ve `Tick()`.
- [x] Type-safe postfix `?` ile `Result<T, E>` hata yayılımı (`cpp`, `js`,
  `python`; operand, enclosing return ve error-type diagnostics dahil).
- [x] Array ve struct destructuring declarations (`let [a, b] = values`,
  `let Point(x, y) = point`; tek değerlendirme, bounds/arity diagnostics ve
  Python/Nyx HIR parity dahil).
- [ ] Birinci sınıf tuple tipiyle tuple destructuring sözleşmesi.
- [ ] Slice/rest patterns: `[head, ..tail]`.
- [ ] Tail-expression block'ları; gereksiz `return` kullanımını azalt.
- [ ] Closure/lambda ifadeleri ve capture kuralları.
- [x] `Array<T>` ve `string` üzerinde doğrudan `for item in collection`.
- [ ] Iterator protokolü ve `yield`.
- [ ] Compile-time `when` ile target/capability seçimi.
- [ ] Public modül yüzeyi için tek bir `pub` görünürlük sözleşmesi.
- [ ] Generic constraint/trait bound yazımı; başarısız constraint için okunaklı
  diagnostic.
- [x] Default argument değerleri: eksik argümanlar, parametre varsayılan ifadesiyle
  çağrı yerinde doldurulur (cpp/js/python runtime parity + E2007/E2003 tanı).
- [ ] Named arguments (isimli argümanlar) sözdizimi ve değerlendirme sırası.
- [ ] `select` ancak Channel/Task semantiği backendler arasında eşitlenirse ekle.

## Standart kütüphane ve proje kullanımı

- [x] C++ namespace/header, Node.js module ve Python module için açık alias'lı
  foreign import sözdizimini parser, typed HIR ve üç emitter'da çalıştır.
- [x] Foreign API binding manifesti ekle; parametre/dönüş türlerini `any` yerine
  HIR'da doğrula ve zincir dışı foreign değerleri güvenle sakla.
- [ ] Rust crate resolution ve `import rust` lowering'ini tamamlayıp ilgili
  `E1413` geliştirme kapısını gerçek entegrasyonla değiştir.
- [x] WASM host fonksiyonlarını versioned `extern "WASM:<namespace>"` ABI ile
  typed HIR'a indir; `nyx_host_v1` sözleşmesini `std/web` ile doğrula.
- [x] Typed `map`, `filter` ve left-to-right `fold` API'lerini contextual lambda
  typing ile `cpp`, `js` ve `python` hedeflerinde tamamla; desteklenmeyen
  backendlerde capability hatası üret.
- [ ] Iterator ve slice semantiğini tamamla; koleksiyon işlemlerini keyword değil
  stdlib fonksiyonu/protokolü olarak tut.
- [x] `std/fs` okuma/yazma/ekleme/silme hata dönüşlerini typed `Result<T,E>`
  modeline taşı; boş dosya ile I/O hatasını üç backendde ayırt et.
- [x] `std/encoding` decode ve `std/json_lite` alan erişimi hatalarını typed
  `Result<T,E>` modeline taşı; geçersiz veri ile geçerli boş/0 değerini ayır.
- [x] Süreç, ağ ve zaman modüllerindeki başarısız işlem/geçersiz girdi
  dönüşlerini `Result` modeline taşı; TCP EOF ile receive hatasını ayır.
- [x] `std/json_lite` sözleşmesini yalnız düz üst-seviye string/int alan
  ayıklayıcı olarak sınırla; genel JSON parser olduğu izlenimini kaldır.
- [x] Paket manifesti, lockfile ve recursive local path dependency çözümünü
  içerik checksum'ları ve cycle diagnostics ile deterministik yap.
- [ ] En az üç gerçek örnek uygulama: CLI aracı, WASM modülü ve küçük servis.

## v4.0.0-rc.2 Bodhi — Web/WASM ekosistemi

- [x] `nyx build --target wasm` ile `.wat`, `.wasm`, `.mjs` ve `.d.ts`
  artifactlarını tek build dizininde üret.
- [x] WASM iç fonksiyon çağrılarında UTF-8 literal ve string parametrelerini
  internal `ptr, len` ABI üzerinden geçir; string dönüş zincirini koru.
- [x] WASM backendinde `Array<int/float>` iteration, `Array/string.len()` method
  çağrıları, internal string call zinciri ve string conditional lowering'i tamamla.
- [x] Versioned `nyx_host_v1` WASM host-import ABI ve capability diagnostics ekle.
- [x] Typed `std/web` DOM handle, attribute, event, Canvas ve lifecycle API'sini ekle.
- [x] npm-ready `package.json`, conditional `exports`, `types`, ESM ve React 19,
  Vue 3, Svelte 5 adaptör çıktılarını üret.
- [x] Nyx Pong'un tarayıcı sürümünü `std/web` üzerinden, elle yazılmış uygulama
  JavaScript'i olmadan çalıştır.
- [ ] JSX/HTML ve reactivity sözdizimini ayrı RFC olarak değerlendir; host ABI
  kararlı olmadan grammar'a ekleme.

RC2 bilinçli sınırı: arbitrary user-defined struct/method ABI, heap-owned string
local'ları, DOM diffing ve JSX grammar bu pakete dahil değildir. Bunlar ABI v2
veya sonraki major RFC gerektirir; desteklenmeyen kullanım sessiz yanlış kod
yerine derleme tanısı üretir.

## Tooling

- [x] Formatter'ı yeni grammar ile idempotent tut.
- [x] LSP completion listesini compiler'ın canonical language surface'inden
  üret; ölü keyword ve olmayan stdlib sembolü yayınlama.
- [ ] Rename, references ve semantic token desteği ekle.
- [ ] VS Code Run/Build/Check komutlarını default native target ile doğrula.
- [ ] Compiler diagnostic'lerini kısa hata, açıklama ve düzeltme önerisi olarak
  standardize et.

## v4.0.0-rc.1 kapıları

- [x] Embedded kaldırma sonrası birleşik test bataryasını %100 geçir.
- [ ] Temiz Windows/Linux/macOS x64 ve macOS arm64 paketleme-soak matrisini çalıştır.
- [x] Stable backendlerin HIR, runtime parity ve capability negatif kapılarını geçir.
- [x] HIR, compiler API, plugin API, Bundle ABI, host ABI ve lockfile
  uyumluluk politikasını yayınla.
- [ ] Checksum, provenance/SBOM ve rollback prosedürünü doğrula.
- [ ] Temiz checkout'ta release auditini iki kez geçir.
- [x] Product Owner onayından sonra `4.0.0-rc.1` etiketini oluştur.

## v4.0.0 Nirvana stable kapıları

- [ ] RC soak süresini blocker olmadan tamamla.
- [ ] Belgelenen syntax ve backend sözleşmelerini stable olarak dondur.
- [ ] Kurulum, örnek projeler, LSP ve paketleme yollarını temiz makinelerde doğrula.
- [ ] Product Owner kararıyla `v4.0.0 Nirvana` yayınını oluştur.
