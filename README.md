# 👟 Alabileceğin Her Şey - Discord Teknik Destek Botu 🚀

Bu proje, "Alabileceğin Her Şey" adlı çevrimiçi ayakkabı mağazası için geliştirilmiş, Python tabanlı akıllı bir Discord teknik destek botudur. Müşteri memnuniyetini en üst düzeye çıkarmak için SSS (Sıkça Sorulan Sorular) otomasyonu ve uzman departmanlara (Programcılar & Satış) yönlendirme sağlayan bilet (ticket) sistemi içerir.

Bu çalışma, Python dilinin 3. seviye (Level 3) asenkron programlama, API entegrasyonu ve yerel veri tabanı yönetimi konularını kapsayan bir mezuniyet projesidir.

---

## 🧠 Proje Geliştirme Değerlendirmesi (Geliştirici Notları)

Proje tasarım ve kodlama sürecindeki durum analizi aşağıda belirtilmiştir:

### ♻️ Eski projelerden kopyalayabileceğiniz kod parçaları var mı?
**Evet, var.** Botun çalışmasını sağlayan ana iskelet yapısı önceki eğitim seviyelerinden (Python Basic ve Pro) aktarılmıştır:
* Kütüphane içe aktarımları (`import discord`).
* Botun sunucuya bağlanmasını sağlayan `on_ready` fonksiyonu ve `bot.run(TOKEN)` blokları.
* Temel `@bot.tree.command` (Slash komutu) yapısının başlangıç iskeleti.
* Intents (yetki) tanımlamalarının standart bölümleri.

### 🏗️ Sıfırdan yazmanız gereken bölümler neler?
Projeyi özgün kılan ve mağazanın ihtiyaçlarına göre **tamamen sıfırdan** kodlanan alanlar şunlardır:
* **UI (Arayüz) Bileşenleri:** Müşteri SSS açılır menüsü (`discord.ui.Select`) ve uzmanlara bilet gönderme formları (`discord.ui.Modal`).
* **Veri Tabanı Şeması:** Talepleri kalıcı olarak saklayan yerel `sqlite3` entegrasyonu ve SQL tablolarının (CRUD) oluşturulması.
* **Akıllı Metin Analizi:** Müşterilerin sohbet kanalına yazdığı "hasarlı", "iptal", "kargo nerede" gibi cümleleri tarayıp mağaza politikasına göre anında yanıt veren algoritma.
* **DM (Özel Mesaj) Bildirim Sistemi:** Bilet kapatıldığında müşteriye arka planda özel mesaj gönderen log sistemi.

### 🤝 Hangi konularda kesinlikle yardıma ihtiyaç duyacaksınız, hangilerini kendi başınıza halledebilirsiniz?
* **Kendi Başıma Halledilebilecekler:** Temel Discord komutlarının oluşturulması, SSS listesindeki soruların kod içine sözlük (dictionary) olarak gömülmesi, veri tabanı okuma/yazma işlemleri ve botun arayüz tasarımları.
* **Yardıma İhtiyaç Duyulan Konular (Zorluklar):** * Asenkron işlemler sırasında API'nin 3 saniye zaman aşımı kuralını aşmak (örn. `interaction.response.defer()` kullanımı).
  * Kullanıcıların DM (Özel Mesaj) kutusu kapalı olduğunda botun çökmesini engelleyen hata yakalama blokları (`try-except discord.Forbidden`).
  * Karmaşık Discord izinleri ve sunucu (Guild) dışı kullanıcı ID eşleştirmeleri.

---

## 🌟 Temel Özellikler

1. **🤖 Otomatik Yanıt Sistemi:** Önceden tanımlanmış Google Dokümanı SSS verilerini kullanarak kullanıcılara açılır menü üzerinden hızlı çözümler sunar.
2. **📩 Gelişmiş Bilet (Ticket) Sistemi:** Formlar aracılığıyla toplanan sorunları SQLite veri tabanına işler.
3. **💬 Kelime Avcısı (Text Processing):** Sohbet kanalındaki normal yazışmaları analiz edip hasar veya iptal taleplerine resmi mağaza yanıtını döner.
4. **🔔 Otomatik Müşteri Bilgilendirme:** Yöneticiler bir bileti çözüp kapattığında (`/talep_kapat`), bot bilet sahibine DM atarak "Talebiniz gerçekleştirildi ve ayakkabınız onarıldı. ✨" mesajını şık bir görsel kartla iletir.

---

## 🛠️ Kurulum ve Çalıştırma

**1. Gerekli Kütüphaneler:**
Bilgisayarınızda Python 3.8+ yüklü olmalıdır. Terminalden Discord kütüphanesini indirin:
```bash
pip install discord.py
