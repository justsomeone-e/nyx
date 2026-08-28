# 📝 Nyx — Master TODO List & Görev Takibi

Bu dosya, **`Nyx`** dilinin sıfırdan zirveye adım adım inşa edilme planıdır.

---

## 🟢 FAZ 1: ÇEKİRDEK DERLEYİCİ & C++ ÇIKTISI (BASİT)
- [ ] **1.1 Lexer (Tokenizer - Kelime Ayıklayıcı):**
  - [ ] Sayılar (`int`: `42`, `float`: `3.14`).
  - [ ] Metinler (`str`: `"Hello World"`).
  - [ ] Boolean (`bool`: `true`, `false`).
  - [ ] Anahtar Kelimeler: `var`, `print`, `fn`, `return`, `if`, `else`, `loop`.
  - [ ] Operatörler: `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`.
- [ ] **1.2 Parser (Sözdizimi Ağacı / AST):**
  - [ ] Değişken tanımlama ve atama (`var x = 10 + 5`).
  - [ ] Ekrana yazdırma ifadesi (`print("X degeri:", x)`).
- [ ] **1.3 C++ Kod Üretici (CodeGen C++):**
  - [ ] `.he` kodunu geçerli, hatasız `output.cpp` dosyasına dönüştürme.
  - [ ] Otomatik derleme: `g++ output.cpp -o program.exe` çalıştırma.

---

## 🟡 FAZ 2: FONKSİYONLAR, DÖNGÜLER & JAVA / JS ÇIKTISI (ORTA)
- [ ] **2.1 Fonksiyon Motoru:**
  - [ ] Fonksiyon tanımlama: `fn add(a: int, b: int) -> int: return a + b`
  - [ ] Fonksiyon çağırma ve dönüş değerini değişkene atama.
- [ ] **2.2 Kontrol Akışı:**
  - [ ] `if condition:` ve `else:` blokları.
  - [ ] `loop condition:` (While döngüsü) ve `for i in 1..10:` (Sayı döngüsü).
- [ ] **2.3 Çoklu Hedef Yönlendirici (#target):**
  - [ ] `#target cpp` $\to$ C++ çıktısı üretir.
  - [ ] `#target java` $\to$ `Output.java` çıktısı üretir.
  - [ ] `#target js` $\to$ `output.js` çıktısı üretir.

---

## 🌐 FAZ 3: WEB UI & HTML/CSS DERLEYİCİSİ (WEB DSL)
- [ ] **3.1 Web Sözdizimi Ayrıştırıcı:**
  - [ ] `ui Page:`, `box [...]`, `title "..."`, `btn "..." [onClick: ...]`.
- [ ] **3.2 HTML5 & CSS3 Üretici:**
  - [ ] Otomatik `index.html` oluşturma.
  - [ ] Köşeli parantezdeki `[bg, color, padding, radius]` özelliklerini `style.css`'e çevirme.
  - [ ] Buton tıklama olaylarını `app.js`'e bağlama.

---

## 🔴 FAZ 4: VERİ YAPILARI & DOĞRUDAN KOD GÖMME (ZOR)
- [ ] **4.1 Listeler ve Diziler:**
  - [ ] `var numbers = [10, 20, 30, 40]` $\to$ C++ `std::vector`, Java `ArrayList`, JS `Array`.
- [ ] **4.2 Struct / Veri Tipleri:**
  - [ ] `struct Player: var name: str, var hp: int`
- [ ] **4.3 Escape Hatch (Doğrudan C++/Java Kodu Yapıştırma):**
  - [ ] `inline cpp: ...` bloğu ile saf C++ kodunu doğrudan geçirme.

---

## 👑 FAZ 5: GELİŞTİRİCİ ARAÇLARI & OFFLINE REHBER (UZMAN)
- [ ] **5.1 Komut Satırı Arayüzü (CLI):**
  - [ ] `he run main.he` (Tek komutla derleyip çalıştırır).
  - [ ] `he build main.he --target cpp` (Sadece C++ çıktısı verir).
  - [ ] `he docs` / `he help` (İnternetsiz, yerleşik dil kılavuzunu açar).
- [ ] **5.2 VS Code Sözdizimi Renklendirmesi (.he Syntax Highlighting):**
  - [ ] VS Code için `.tmLanguage.json` eklenti paketi.
