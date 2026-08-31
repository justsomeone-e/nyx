# Nyx v4 Development TODO

Bu dosya Nyx v4 geliştirme hattının aktif görev listesidir. `v4.0.0 Nirvana`
stable sürümü henüz yayınlanmadı; beta ve RC etiketleri ancak aşağıdaki kapılar
gerçekten tamamlandığında oluşturulacaktır.

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
- [ ] Birincil geliştirme hedeflerini `cpp` native ve `wasm` olarak belirle;
  diğer backendleri açık capability sözleşmeleriyle koru.

## Compiler çekirdeği

- [ ] `nyx build/run` için host-native varsayılanını tamamla; kaynak dosyada
  `#target` zorunluluğunu kaldır ve CLI/manifest override sırasını dondur.
- [ ] Python ve Nyx frontendlerinin lexer, parser, typechecker ve canonical HIR
  parity kapısını her syntax değişikliğinde zorunlu tut.
- [ ] HIR verifier hata kodlarını ve source-span davranışını public sözleşme yap.
- [ ] C++ emitter'ın yalnız kullanılan runtime parçalarını üretmesini sağla;
  gereksiz include ve boilerplate maliyetini ölç.
- [ ] Stage 1 -> Stage 2 -> Stage 3 self-host zincirini temiz checkout'ta iki
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
- [ ] Payload enum: `enum Result<T, E> { Ok(T), Err(E) }`.
- [ ] `Ok(value)` / `Err(error)` ve enum destructuring pattern'ları.
- [ ] Type-safe `?` ile `Result<T, E>` hata yayılımı.
- [ ] Array, tuple ve struct destructuring declarations.
- [ ] Slice/rest patterns: `[head, ..tail]`.
- [ ] Tail-expression block'ları; gereksiz `return` kullanımını azalt.
- [ ] Closure/lambda ifadeleri ve capture kuralları.
- [ ] Iterator protokolü, `yield` ve doğrudan koleksiyon üzerinde `for`.
- [ ] Compile-time `when` ile target/capability seçimi.
- [ ] Public modül yüzeyi için tek bir `pub` görünürlük sözleşmesi.
- [ ] Generic constraint/trait bound yazımı; başarısız constraint için okunaklı
  diagnostic.
- [ ] Named arguments ve default argument değerlendirme sırasını tanımla.
- [ ] `select` ancak Channel/Task semantiği backendler arasında eşitlenirse ekle.

## Standart kütüphane ve proje kullanımı

- [ ] Koleksiyon API'sini `map`, `filter`, `fold`, iterator ve slice semantiğiyle
  tamamla; bunları keyword değil stdlib fonksiyonu/protokolü olarak tut.
- [ ] Dosya, süreç, ağ, zaman, encoding ve JSON modüllerinde hata dönüşlerini
  `Result` modeline taşı.
- [ ] `std/json_lite` sınırını dürüstçe koru veya gerçek JSON parser ekle;
  substring tabanlı extractor'ı tam JSON gibi sunma.
- [ ] Paket manifesti, lockfile ve local dependency çözümünü deterministik yap.
- [ ] En az üç gerçek örnek uygulama: CLI aracı, WASM modülü ve küçük servis.

## Tooling

- [ ] Formatter'ı yeni grammar ile idempotent tut.
- [ ] LSP completion listesini compiler'ın canonical language surface'inden
  üret; ölü keyword ve olmayan stdlib sembolü yayınlama.
- [ ] Rename, references ve semantic token desteği ekle.
- [ ] VS Code Run/Build/Check komutlarını default native target ile doğrula.
- [ ] Compiler diagnostic'lerini kısa hata, açıklama ve düzeltme önerisi olarak
  standardize et.

## v4.0.0-rc.1 kapıları

- [ ] Embedded kaldırma sonrası birleşik test bataryasını %100 geçir.
- [ ] Temiz Windows/Linux/macOS x64 ve macOS arm64 paketleme-soak matrisini çalıştır.
- [ ] Stable backendlerin HIR, runtime parity ve capability negatif kapılarını geçir.
- [ ] HIR, compiler API, plugin API ve Bundle ABI uyumluluk politikasını yayınla.
- [ ] Checksum, provenance/SBOM ve rollback prosedürünü doğrula.
- [ ] Temiz checkout'ta release auditini iki kez geçir.
- [ ] Product Owner onayından sonra `4.0.0-rc.1` etiketini oluştur.

## v4.0.0 Nirvana stable kapıları

- [ ] RC soak süresini blocker olmadan tamamla.
- [ ] Belgelenen syntax ve backend sözleşmelerini stable olarak dondur.
- [ ] Kurulum, örnek projeler, LSP ve paketleme yollarını temiz makinelerde doğrula.
- [ ] Product Owner kararıyla `v4.0.0 Nirvana` yayınını oluştur.
