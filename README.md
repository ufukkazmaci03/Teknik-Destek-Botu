readme_content = """# 👟 Alabileceğin Her Şey - Discord Teknik Destek Botu

Bu proje, "Alabileceğin Her Şey" çevrimiçi ayakkabı mağazası için geliştirilmiş, Python tabanlı bir Discord teknik destek botudur. Müşterilerin sıkça sorduğu soruları yanıtlamak, mağaza içi sorunları çözmek ve gerektiğinde talepleri ilgili uzman departmanlara (Programcılar ve Satış Departmanı) yönlendirmek amacıyla tasarlanmıştır.

Bu çalışma, Python dilinin güncel nesne yönelimli ve asenkron programlama teknikleri kullanılarak hazırlanmış bir mezuniyet projesidir.

## 🚀 Özellikler

1. **Otomatik SSS (Sıkça Sorulan Sorular) Menüsü:** Kullanıcılar, modern ve şık bir açılır menü (Select Menu) aracılığıyla mağaza politikaları, sipariş durumları ve iptal/iade süreçleri hakkında anında bilgi alabilirler.
2. **Canlı Destek Formu (Modal Entegrasyonu):** SSS menüsünde aradığı cevabı bulamayan müşteriler, doğrudan Discord arayüzü üzerinden açılan bir form penceresi ile sorunlarını detaylıca iletebilirler.
3. **Akıllı Metin İşleme (Text Processing):** Bot, sohbet kanallarına yazılan "hasarlı", "iptal", "kargom nerede" gibi anahtar kelimeleri otomatik olarak algılar ve kullanıcıyı ilgili çözüme yönlendirir.
4. **Kalıcı Veri Tabanı (SQLite3):** Uzmanlara iletilen tüm destek talepleri, kullanıcı bilgileri, departman türü, mesaj ve tarih damgasıyla birlikte güvenli bir yerel veri tabanında saklanır.
5. **Yönetici Kontrol Paneli:** Mağaza yöneticileri `/biletler` ve `/bilet_kapat` gibi gelişmiş eğik çizgi (Slash) komutlarını kullanarak gelen talepleri canlı olarak yönetebilir.

## 🛠️ Gereksinimler

Projenin çalıştırılabilmesi için bilgisayarınızda **Python 3.8 veya üzeri** bir sürümün yüklü olması gerekmektedir. 

Gerekli harici kütüphane:
* `discord.py` (v2.x)

## 📦 Kurulum ve Çalıştırma

1.  **Bağımlılıkları Yükleyin:**
    Komut satırından (CMD / Terminal) aşağıdaki komutu çalıştırarak gerekli kütüphaneyi yükleyin:
    ```
```text?code_stdout&code_event_index=2
README.md başarıyla oluşturuldu.

```bash
    pip install discord.py
    ```

2.  **Discord Geliştirici Portalı Ayarları:**
    * [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin.
    * Bot uygulamanızı seçip sol menüdeki **Bot** sekmesine tıklayın.
    * **Privileged Gateway Intents** başlığı altındaki şu üç seçeneği de aktif hale getirin:
        * *Presence Intent*
        * *Server Members Intent*
        * *Message Content Intent* (Metin işleme ve kelime yakalama için zorunludur)

3.  **Token Yapılandırması:**
    * `bot.py` dosyasını bir kod editöründe açın.
    * Dosyanın en altında yer alan `BOT_TOKEN = "BURAYA_DISCORD_BOT_TOKENINIZI_YAZIN"` satırındaki tırnak işaretlerinin arasına kendi bot tokenınızı yapıştırın.

4.  **Projeyi Başlatın:**
    Terminal üzerinden projeyi çalıştırın:
    ```bash
    python bot.py
    ```

## 🎯 Kullanım Kılavuzu

### Müşteriler İçin:
* **`/yardim`**: Teknik destek merkezini, SSS açılır menüsünü ve departman butonlarını içeren ana paneli ekrana getirir.
* **Doğrudan Mesajlaşma**: Sohbet kanallarına "Siparişim hasarlı geldi" gibi cümleler veya anahtar kelimeler yazıldığında bot otomatik olarak devreye girer.

### Mağaza Yöneticileri İçin:
* **`/biletler`**: Şu anda sistemde bekleyen ve henüz çözülmemiş olan tüm açık destek biletlerini listeler.
* **`/bilet_kapat [bilet_id]`**: Sorunu çözülen biletin durumunu veri tabanında "Kapalı" olarak günceller (Örn: `/bilet_kapat bilet_id: 1`).

## 🗄️ Veri Tabanı Şeması (`magaza_destek.db`)

Sistem ilk kez çalıştırıldığında otomatik olarak `biletler` adında bir tablo oluşturur. Tablo yapısı şu şekildedir:

| Kolon Adı | Veri Tipi | Açıklama |
| :--- | :--- | :--- |
| `id` | INTEGER (PK) | Her bilet için otomatik artan benzersiz numara |
| `kullanici_id` | TEXT | Bileti açan üyenin Discord ID'si |
| `kullanici_adi` | TEXT | Bileti açan üyenin Discord kullanıcı adı |
| `departman` | TEXT | Talebin iletildiği birim (Programcılar / Satış) |
| `sorun_mesaji` | TEXT | Kullanıcının formda belirttiği detaylı şikayet |
| `durum` | TEXT | Biletin güncel durumu (Varsayılan: 'Açık') |
| `tarih` | TEXT | Talebin oluşturulduğu tam zaman damgası |

## 📁 Proje Yapısı

```text
├── bot.py               # Ana uygulama ve bot kaynak kodu
├── magaza_destek.db     # Otomatik oluşturulan SQLite veri tabanı dosyası
└── README.md            # Proje açıklama ve kullanım dokümanı
