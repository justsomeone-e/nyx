# 📋 HolyEasyLang (heLang) — Master Kanban & Geliştirme Yol Haritası

Bu Kanban panosu, **`HolyEasyLang`** dilini adım adım, sağlam temeller üzerine kurarak profesyonel bir derleyiciye dönüştürmek için hazırlanmıştır.

---

## 🗂️ KANBAN PANOSU

```
┌───────────────────────────┬───────────────────────────┬───────────────────────────┬───────────────────────────┐
│       📝 YAPILACAKLAR     │      ⚙️ DEVAM EDENLER     │      🔍 TEST AŞAMASI      │       ✅ TAMAMLANANLAR    │
│          (TODO)           │       (IN PROGRESS)       │         (TESTING)         │           (DONE)          │
├───────────────────────────┼───────────────────────────┼───────────────────────────┼───────────────────────────┤
│ • Struct / Sınıf Yapısı   │ • Temel Lexer (Kelimeler) │ • Değişken Tanımlama      │ • Proje Mimarisi Belirlendi│
│ • Listeler ve Diziler     │ • Temel Parser (Sözdizimi)│ • Ekrana Yazdırma (Print) │ • Kanban Yol Haritası     │
│ • Dış Kütüphane Köprüsü   │ • C++ CodeGen (Çıktı)     │                           │                           │
└───────────────────────────┴───────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

## 🎯 SEVİYE SEVİYE GÖREV LİSTESİ (ROADMAP)

### 🟢 1. SEVİYE: BASİT (Temel Sözdizimi & İlk Çıktı)
- [ ] **1.1 Lexer (Tokenizer):** 
  - Sayılar (`123`, `45.6`), Metinler (`"merhaba"`), Değişken isimleri (`x`, `sayi`).
  - Temel anahtar kelimeler: `var`, `fn`, `ret`, `yazdir` / `print`.
  - Operatörler: `+`, `-`, `*`, `/`, `=`, `==`, `<`, `>`.
- [ ] **1.2 Parser (AST Ağacı):**
  - Değişken atama: `var a = 10` $\to$ C++: `int a = 10;`
  - Ekrana yazdırma: `yazdir("Sonuc:", a + 5)` $\to$ C++: `std::cout << ...`
- [ ] **1.3 C++ Çıktı Üretici (CodeGen C++):**
  - `.he` dosyasını okuyup çalışan `output.cpp` üretmesi ve `g++` ile derlenmesi.

---

### 🟡 2. SEVİYE: ORTA (Fonksiyonlar & Kontrol Akışı)
- [ ] **2.1 Fonksiyon Tanımlama & Çağırma:**
  - `fn topla(a: int, b: int) -> int:` $\to$ `int topla(int a, int b) { return a + b; }`
- [ ] **2.2 Karar Yapıları:**
  - `eger kosul:` / `degilse:` $\to$ `if (kosul) { ... } else { ... }`
- [ ] **2.3 Döngüler:**
  - `dongu kosul:` $\to$ `while (kosul) { ... }`
  - `tekrar 1..10:` $\to$ `for (int i = 1; i <= 10; i++) { ... }`
- [ ] **2.4 Java & Kotlin Hedefleri:**
  - Aynı AST ağacından `Output.java` ve `Output.kt` dosyalarını da çıkarabilme.

---

### 🔴 3. SEVİYE: ZOR (Veri Yapıları & Modüller)
- [ ] **3.1 Diziler ve Listeler:**
  - `var sayilar = [1, 2, 3, 4]` $\to$ `std::vector<int> sayilar = {1, 2, 3, 4};`
- [ ] **3.2 Struct / Tip Tanımlama:**
  - `tip Oyuncu: var can: int, var isim: str`
- [ ] **3.3 Modül Sistemi:**
  - `import "matematik.he"` ile diğer `.he` dosyalarını projeye dahil etme.

---

### 👑 4. SEVİYE: UZMAN (Evrensel Kütüphane & VS Code Eklentisi)
- [ ] **4.1 Dış Dil Kütüphane Import:**
  - `import cpp "raylib.h"`, `import java "java.util.*"`, `import py "numpy"`.
- [ ] **4.2 Otomatik C-Bridge / JNI Köprüsü:**
  - Diller arası veri tipi dönüşümlerini (String $\leftrightarrow$ char*, List $\leftrightarrow$ ArrayList) otomatik yapma.
- [ ] **4.3 VS Code Eklentisi:**
  - `.he` dosyaları için renkli sözdizimi (Syntax Highlighting) paketi!
