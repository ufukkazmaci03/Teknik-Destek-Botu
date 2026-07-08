import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime

# ==========================================
# 1. VERİ TABANI AYARLARI VE BAŞLATMA
# ==========================================
def veri_tabani_olustur():
    """Botun çalışması için gerekli yerel SQLite veri tabanını ve biletler tablosunu kurar."""
    conn = sqlite3.connect('magaza_destek.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS talepler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kullanici_id TEXT NOT NULL,
                    kullanici_adi TEXT NOT NULL,
                    departman TEXT NOT NULL,
                    mesaj TEXT NOT NULL,
                    durum TEXT DEFAULT 'Açık',
                    tarih TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Bot başlamadan önce veri tabanını hazır hale getiriyoruz
veri_tabani_olustur()


# ==========================================
# 2. BOT YAPILANDIRMASI VE INTENTS AYARLARI
# ==========================================
# Gereksinim 3: Normal metin mesajlarını okuyup işleyebilmek için Message Content yetkisi açık olmalıdır.
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# 3. INTERAKTIF ARAYÜZ BİLEŞENLERİ (UI)
# ==========================================
# Gereksinim 4: Kullanıcılar için anlaşılır, modern ve çekici modal/buton/menü tasarımları.

class DestekModali(discord.ui.Modal, title="Teknik Destek Formu"):
    """Kullanıcının sorununu detaylıca yazıp uzmana ilettiği açılır pop-up pencere."""
    def __init__(self, departman):
        super().__init__()
        self.departman = departman

    # Form elemanları
    siparis_no = discord.ui.TextInput(
        label="Sipariş Numarası (İsteğe Bağlı)", 
        required=False, 
        placeholder="Örn: 987654",
        max_length=20
    )
    detay = discord.ui.TextInput(
        label="Sorununuzu/Talebinizi Detaylıca Açıklayın", 
        style=discord.TextStyle.paragraph, 
        placeholder="Lütfen ayakkabı modeli veya karşılaştığınız hatayı buraya yazın...", 
        required=True,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Kullanıcı formu gönderdiğinde çalışır ve veriyi SQLite veri tabanına kaydeder."""
        kullanici = interaction.user
        su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tam_mesaj = f"Sipariş No: {self.siparis_no.value if self.siparis_no.value else 'Belirtilmedi'} | Detay: {self.detay.value}"

        # Gereksinim 2: Veri tabanı entegrasyonu ile talebi saklama
        conn = sqlite3.connect('magaza_destek.db')
        c = conn.cursor()
        c.execute("INSERT INTO talepler (kullanici_id, kullanici_adi, departman, mesaj, tarih) VALUES (?, ?, ?, ?, ?)",
                  (str(kullanici.id), kullanici.name, self.departman, tam_mesaj, su_an))
        conn.commit()
        talep_id = c.lastrowid
        conn.close()

        # Kullanıcıya işlemin başarılı olduğuna dair şık bir Embed gönderilir
        embed = discord.Embed(
            title="✅ Destek Talebiniz Başarıyla Alındı!",
            description=f"Merhaba **{kullanici.name}**, talebiniz ilgili uzman ekibimize ulaştırılmıştır.",
            color=discord.Color.green()
        )
        embed.add_field(name="Talep ID", value=f"#{talep_id}", inline=True)
        embed.add_field(name="Departman", value=self.departman, inline=True)
        embed.add_field(name="İletilen Mesaj", value=self.detay.value, inline=False)
        embed.set_footer(text="Alabileceğin Her Şey - Müşteri Destek Sistemi")

        await interaction.response.send_message(embed=embed, ephemeral=True)


class SSSDropdown(discord.ui.Select):
    """Gereksinim 1: Belgede yer alan Sıkça Sorulan Soruları otomatik yanıtlayan açılır menü."""
    def __init__(self):
        options = [
            discord.SelectOption(label="Nasıl alışveriş yapabilirim?", value="alisveris", description="Satın alma adımları rehberi", emoji="🛍️"),
            discord.SelectOption(label="Siparişimin durumunu nasıl öğrenebilirim?", value="durum", description="Kargo ve sipariş takibi", emoji="📦"),
            discord.SelectOption(label="Bir siparişi nasıl iptal edebilirim?", value="iptal", description="Sipariş iptal koşulları", emoji="❌"),
            discord.SelectOption(label="Siparişim hasarlı gelirse ne yapmalıyım?", value="hasar", description="Hasarlı ürün bildirim süreci", emoji="⚠️"),
            discord.SelectOption(label="Teknik destekle nasıl iletişime geçebilirim?", value="teknik", description="İletişim kanallarımız", emoji="📞"),
            discord.SelectOption(label="Teslimat yöntemini değiştirebilir miyim?", value="teslimat", description="Ödeme anında teslimat ayarı", emoji="🚚")
        ]
        super().__init__(placeholder="Merak ettiğiniz bir konuyu buradan seçin...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        """Kullanıcı menüden bir soru seçtiğinde tetiklenen mekanizma."""
        secilen = self.values[0]
        
        # Google Dokümanı içindeki resmi cevapların birebir entegrasyonu
        sss_cevaplar = {
            "alisveris": "Alışveriş yapmak için, ilgilendiğiniz ürünü seçip 'Alışveriş Sepetine Ekle' butonuna tıklayın. Ardından Alışveriş Sepetine gidin ve satın alma işlemini tamamlamak için yönergeleri takip edin.",
            "durum": "Siparişinizin durumunu öğrenmek için internet sitemizdeki hesabınıza giriş yapın ve 'Siparişlerim' bölümüne gidin. Orada, siparişinizin mevcut durumunu görebilirsiniz.",
            "iptal": "Siparişinizi iptal etmek istiyorsanız, lütfen en kısa sürede müşteri hizmetlerimizle iletişime geçin. Siparişiniz gönderilmeden önce iptal işleminizde size yardımcı olmaya çalışacağız.",
            "hasar": "Hasarlı bir ürün aldıysanız, lütfen hemen müşteri hizmetlerimizle iletişime geçin ve hasarın fotoğraflarını sağlayın. Ürünü değiştirmeniz veya iade etmeniz konusunda size yardımcı olacağız.",
            "teknik": "Teknik destekle, internet sitemizde yer alan telefon numarasını arayarak iletişime geçebilirsiniz. Alternatif olarak, sohbet robotumuz üzerinden de bizimle iletişim kurabilirsiniz.",
            "teslimat": "Evet, ödeme sayfasında teslimat bilgilerini değiştirebilirsiniz. Kullanılabilir teslimat yöntemleri ve şartları orada listelenecektir."
        }

        soru_metni = [o.label for o in self.options if o.value == secilen][0]
        cevap_metni = sss_cevaplar.get(secilen, "Açıklama bulunamadı.")

        embed = discord.Embed(
            title=f"❓ {soru_metni}",
            description=cevap_metni,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Aradığınız yanıtı bulamadıysanız aşağıdaki butonlarla uzmanlara bağlanabilirsiniz.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


class DestekPaneliGörunumu(discord.ui.View):
    """Dropdown menüyü ve uzman departman butonlarını tek çatı altında toplayan ana panel."""
    def __init__(self):
        super().__init__(timeout=None) # Panelin süresinin dolmaması için
        self.add_item(SSSDropdown())

    @discord.ui.button(label="💻 Programcı Desteği (Site / Ödeme)", style=discord.ButtonStyle.danger, row=1)
    async def programci_buton(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Programcı ekibine iletilecek formu açar
        await interaction.response.send_modal(DestekModali(departman="Programcılar"))

    @discord.ui.button(label="👟 Satış Departmanı (Ürün / Numara)", style=discord.ButtonStyle.success, row=1)
    async def satis_buton(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Satış ekibine iletilecek formu açar
        await interaction.response.send_modal(DestekModali(departman="Satış Departmanı"))


# ==========================================
# 4. SÖZCÜK ANALİZİ VE METİN İŞLEME (TEXT PROCESSING)
# ==========================================
# Gereksinim 3: Botun doğrudan normal sohbet akışını filtreleyerek akıllı yanıtlar üretebilmesi.

@bot.event
async def on_message(message: discord.Message):
    """Kullanıcıların kanallara yazdığı normal mesajları tarar ve tetikleyici kelimeleri yakalar."""
    if message.author.bot:
        return

    mesaj_kucuk = message.content.lower()

    # Akıllı kelime eşleştirme senaryoları
    if "hasarlı" in mesaj_kucuk or "yırtık" in mesaj_kucuk or "hasar" in mesaj_kucuk:
        embed = discord.Embed(
            title="⚠️ Hasarlı Ürün Yardımı",
            description="Mesajınızda hasarlı ürün ifadesi tespit edildi.\n\n**Çözüm:** Hasarlı bir ürün aldıysanız, lütfen hemen müşteri hizmetlerimize hasar fotoğraflarını sağlayın. İade veya değişim sürecini anında başlatalım.\n\nDetaylı form açmak için lütfen `/yardim` komutunu kullanın.",
            color=discord.Color.orange()
        )
        await message.reply(embed=embed)
        return

    elif "iptal" in mesaj_kucuk and "sipariş" in mesaj_kucuk:
        embed = discord.Embed(
            title="❌ Sipariş İptal İşlemleri",
            description="Sipariş iptaliyle ilgili otomatik bilgilendirme:\n\n**Çözüm:** Siparişiniz kargoya verilmeden önce iptal etmek istiyorsanız en kısa sürede bizimle iletişime geçmelisiniz. Kargolanmış ürünlerde iptal yerine kapıda iade hakkınızı kullanabilirsiniz.",
            color=discord.Color.orange()
        )
        await message.reply(embed=embed)
        return

    elif "kargom" in mesaj_kucuk or "sipariş durumu" in mesaj_kucuk:
        embed = discord.Embed(
            title="📦 Sipariş Durumu Sorgulama",
            description="Sipariş takibiyle ilgili otomatik bilgilendirme:\n\n**Çözüm:** Siparişinizin durumunu öğrenmek için internet sitemizdeki hesabınıza giriş yapın ve 'Siparişlerim' bölümüne göz atın.",
            color=discord.Color.orange()
        )
        await message.reply(embed=embed)
        return

    # Komutların arka planda çalışmaya devam edebilmesi için zorunlu satır
    await bot.process_commands(message)


# ==========================================
# 5. EĞİK ÇİZGİ (SLASH) KOMUTLARI
# ==========================================

@bot.tree.command(name="yardim", description="Alabileceğin Her Şey teknik destek panelini açar.")
async def yardim_komutu(interaction: discord.Interaction):
    """Müşterilerin kullanacağı interaktif ana paneli ekrana getirir."""
    embed = discord.Embed(
        title="👟 Alabileceğin Her Şey - Teknik Destek Merkezi",
        description="Mağazamıza hoş geldiniz! Yaşadığınız sorunları hızlıca çözmek için aşağıdaki açılır menüden otomatik yanıtları inceleyebilir ya da doğrudan ilgili uzman birimlerimize destek bileti gönderebilirsiniz.",
        color=discord.Color.gold()
    )
    embed.add_field(name="🤖 Otomatik SSS Sistemi", value="Açılır menüyü kullanarak belgelenmiş resmi çözümlere anında ulaşın.", inline=False)
    embed.add_field(name="💻 Programcılar", value="İnternet sitesi teknik hataları ve ödeme sistemi problemleri için.", inline=True)
    embed.add_field(name="👟 Satış Departmanı", value="Markamıza ait ayakkabıların ürün bilgisi, numara ve kargo sorunları için.", inline=True)
    embed.set_footer(text="Geliştirici: Ufuk Kazmacı (No: 559)")
    
    await interaction.response.send_message(embed=embed, view=DestekPaneliGörunumu())


@bot.tree.command(name="talepler", description="[Yönetici] Sistemde bekleyen aktif tüm açık destek biletlerini listeler.")
async def talepleri_listele(interaction: discord.Interaction):
    """Yöneticilerin veri tabanındaki açık biletleri görmesini sağlar."""
    # 1. ADIM: Discord'a hemen yanıt sürecini ertelemesini söylüyoruz (Zaman aşımını önler)
    await interaction.response.defer(ephemeral=True)

    conn = sqlite3.connect('magaza_destek.db')
    c = conn.cursor()
    c.execute("SELECT id, kullanici_adi, departman, mesaj, tarih FROM talepler WHERE durum='Açık'")
    veriler = c.fetchall()
    conn.close()

    if not veriler:
        # Önceden 'send_message' kullanıyorduk, defer kullandığımız için artık 'followup.send' kullanmalıyız
        await interaction.followup.send("🎉 Şu anda sistemde çözüm bekleyen açık bir talep bulunmuyor!", ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 Aktif Müşteri Destek Talepleri",
        description="Aşağıdaki biletler uzman müdahalesi beklemektedir:",
        color=discord.Color.purple()
    )

    for bilet in veriler:
        bilet_id, k_adi, boru, msg, zaman = bilet
        embed.add_field(
            name=f"Bilet #{bilet_id} — Müşteri: {k_adi}",
            value=f"**Departman:** {boru}\n**Tarih:** {zaman}\n**İçerik:** {msg}\n" + "—"*15,
            inline=False
        )

    # Burayı da 'followup.send' olarak güncelliyoruz
    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="talep_kapat", description="[Yönetici] Çözülen bir talebi kapatır ve müşteriye otomatik DM gönderir.")
@app_commands.describe(bilet_id="Kapatılacak olan biletin benzersiz ID numarası")
async def talebi_kapat(interaction: discord.Interaction, bilet_id: int):
    """Veri tabanından bilet sahibini bulur, talebi kapatır ve müşteriye DM atar."""
    # Discord zaman aşımını (3 saniye kuralını) engellemek için işlemi erteliyoruz
    await interaction.response.defer(ephemeral=True)

    conn = sqlite3.connect('magaza_destek.db')
    c = conn.cursor()
    
    # 1. ADIM: Veri tabanından biletin sahibinin Discord ID'sini çekiyoruz
    c.execute("SELECT kullanici_id FROM talepler WHERE id=?", (bilet_id,))
    sonuc = c.fetchone()
    
    if not sonuc:
        await interaction.followup.send(f"❌ #{bilet_id} numaralı bir talep veri tabanında bulunamadı.", ephemeral=True)
        conn.close()
        return

    kullanici_id = sonuc[0]

    # 2. ADIM: Talebin durumunu veri tabanında 'Kapalı' olarak güncelliyoruz
    c.execute("UPDATE talepler SET durum='Kapalı' WHERE id=?", (bilet_id,))
    conn.commit()
    conn.close()

    # 3. ADIM: Müşterinin özel mesaj kutusuna (DM) bildirim gönderiyoruz
    dm_notu = "ve müşteriye bilgilendirme mesajı başarıyla iletildi."
    
    try:
        # Discord API'sinden kullanıcı nesnesini ID ile çağırıyoruz
        kullanici = await bot.fetch_user(int(kullanici_id))
        
        # Müşterinin göreceği çok şık bir Embed (Görsel Kart) hazırlıyoruz
        onay_embed = discord.Embed(
            title="👟 Alabileceğin Her Şey - Sipariş Güncellemesi",
            description=f"Merhaba, mağazamıza iletmiş olduğunuz **#{bilet_id}** numaralı destek talebiniz tamamlanmıştır.",
            color=discord.Color.blue()
        )
        # İstediğin mesajı tam buraya ekledik:
        onay_embed.add_field(
            name="🛠️ İşlem Detayı", 
            value="**Talebiniz gerçekleştirildi ve ayakkabınız onarıldı.** ✨", 
            inline=False
        )
        onay_embed.set_footer(text="Markamızı tercih ettiğiniz için teşekkür ederiz! İyi günler dileriz.")
        
        # Mesajı müşterinin DM kutusuna gönderiyoruz
        await kullanici.send(embed=onay_embed)

    except discord.Forbidden:
        # Eğer müşterinin DM kutusu yabancılara kapalıysa botun çökmesini engelliyoruz
        dm_notu = "ancak müşterinin gizlilik ayarları nedeniyle DM kutusu kapalı olduğundan mesaj iletilemedi."
    except Exception as e:
        dm_notu = f"ancak DM gönderilirken bir sorun oluştu: {e}"

    # 4. ADIM: Yöneticiye işlemin bittiğine dair rapor veriyoruz
    await interaction.followup.send(f"✅ #{bilet_id} numaralı talep başarıyla kapatıldı {dm_notu}", ephemeral=True)


# ==========================================
# 6. BOT BAŞLATMA VE SENKRONİZASYON
# ==========================================
@bot.event
async def on_ready():
    """Bot Discord sunucusuna sorunsuz bağlandığında tetiklenir."""
    print(f"--------------------------------------------------")
    print(f"🤖 Bot Aktif: {bot.user.name} | ID: {bot.user.id}")
    
    # Slash komutlarını Discord API sistemine otomatik kaydetme adımı
    try:
        senkronize = await bot.tree.sync()
        print(f"🔄 {len(senkronize)} adet global eğik çizgi komutu başarıyla senkronize edildi.")
    except Exception as e:
        print(f"🚨 Senkronizasyon hatası meydana geldi: {e}")
    print(f"--------------------------------------------------")


# Botunun çalışması için Discord Developer Portal'dan alacağın gizli Token kodunu buraya girmelisin.
BOT_TOKEN = "BURAYA_DISCORD_BOT_TOKENINIZI_YAZIN"

if __name__ == "__main__":
    bot.run(TOKEN)
