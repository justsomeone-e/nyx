# ⚡ Nyx (heLang) Titan Specification Manual v4.0

> **Tasarım Felsefesi:** *"Low-Level gücünü C++'tan, pratikliği Python'dan, web esnekliğini React'tan al; ama hiçbirinin karmaşasını yaşama."*

---

## 1. 🚀 Hızlı Başlangıç & CLI (`he`)

Nyx artık tek bir komut satırı aracıyla (`he`) yönetilir:

```bash
# Programı çalıştır (Live Interactive Runner)
he run main.he

# Hedef dilde kaynak kod üret (C++, React, Python, JS)
he build main.he

# 10/10 Otomatik derleyici testlerini çalıştır
he test

# Yeni bir Nyx projesi başlat
he new my_radar_project
```

---

## 2. 🔀 Pattern Matching (`match ... with`)

Geleneksel `switch-case` veya uzun `if-else` zincirleri yerine **Rust / Scala** tarzı modern eşleştirme:

```he
#target hecpp

enum MetalType {
    Gold = 5000,
    Silver = 8700,
    Bronze = 11300
}

var detected = "Gold"

match detected {
    "Gold" => print("🎯 ALTIN REZONANSI YAKALANDI! (5000 Hz)"),
    "Silver" => print("🥈 GÜMÜŞ REZONANSI YAKALANDI! (8700 Hz)"),
    "_" => print("Zemin Temiz.")
}
```

---

## 3. 🏗️ Structs & Enums (Özel Veri Tipleri)

```he
#target hecpp

struct TargetPoint {
    name,
    frequency,
    signal_strength
}

var point1 = TargetPoint("Oda Mezarı", 700, 92)
print("Nokta:", point1.name, "| Frekans:", point1.frequency, "Hz")
```

---

## 4. 🌊 Boru Hattı (|>) ve Ters Ok (->) Akışları

```he
#target hecpp

5000 -> freq
fn double_val(x) { return x * 2 }

freq |> double_val |> print
```

---

## 5. 🛡️ Güvenli Hata Yönetimi (`try / catch`)

```he
#target hecpp

try {
    var result = 100 / 0
} catch err {
    print("Hata yakalandı:", err)
}
```

---

## 6. 🔍 Düşük Seviye RAM & Donanım Bellek Denetimi

```he
#target hecpp

var secret = 1337
var p = addr(secret)

print("RAM Pointer:", p)
print("RAM Değeri:", peek(p))

// 16 baytlık Hex RAM dökümü
memdump(p, 16)
```

---

## 7. 🎯 Desteklenen Hedef Sistemler (`#target`)

| Direktif | Hedef Çıktı | Kullanım Alanı |
| :--- | :--- | :--- |
| `#target hecpp` | **C++20 (Native)** | Yüksek performans, radar, gömülü sistemler |
| `#target hereact` | **React TSX** | Web arayüzleri, paneller, grafikler |
| `#target hepy` | **Python 3** | Veri analizi, yapay zeka, hızlı otomasyon |
| `#target hejs` | **JavaScript (ES6)** | Web, Node.js, Electron |
| `#target heino` | **Arduino / ESP32** | Donanım yazılımı (Firmware), frekans üreteçleri |

---
*Nyx Titan Engine v4.0 © 2026 - Tüm Hakları Saklıdır.*
