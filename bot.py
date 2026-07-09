import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
import config 

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

veri_tabani_olustur()


# ==========================================
# 2. BOT YAPILANDIRMASI VE INTENTS AYARLARI
# ==========================================
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================================
# 3. INTERAKTIF ARAYÜZ BİLEŞENLERİ (UI)
# ==========================================
class DestekModali(discord.ui.Modal, title="Teknik Destek Formu"):
    def __init__(self, departman):
        super().__init__()
        self.departman = departman

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
        kullanici = interaction.user
        su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tam_mesaj = f"Sipariş No: {self.siparis_no.value if self.siparis_no.value else 'Belirtilmedi'} | Detay: {self.detay.value}"

        # 1. VERİ TABANINA KAYDETME (Aynı kalıyor)
        conn = sqlite3.connect('magaza_destek.db')
        c = conn.cursor()
        c.execute("INSERT INTO talepler (kullanici_id, kullanici_adi, departman, mesaj, tarih) VALUES (?, ?, ?, ?, ?)",
                  (str(kullanici.id), kullanici.name, self.departman, tam_mesaj, su_an))
        conn.commit()
        talep_id = c.lastrowid
        conn.close()

        # 2. MÜŞTERİYE KISA ONAY MESAJI GÖSTERME
        musteri_embed = discord.Embed(
            title="✅ Talebiniz Başarıyla İletildi",
            description=f"Merhaba **{kullanici.name}**, sorununuz uzman ekibimize ulaştı. En kısa sürede sizinle iletişime geçeceğiz.",
            color=discord.Color.green()
        )
        musteri_embed.set_footer(text="Alabileceğin Her Şey - Müşteri Destek Sistemi")
        # Sadece bu mesajı müşteri görür
        await interaction.response.send_message(embed=musteri_embed, ephemeral=True)

        # 3. YÖNETİCİYE (SANA) ÖZEL MESAJ İLE BİLDİRİM GÖNDERME
        try:
            # config.py'den ID'ni çekip seni buluyoruz
            yonetici = await interaction.client.fetch_user(config.YONETICI_ID)
            
            yonetici_embed = discord.Embed(
                title=f"🚨 YENİ BİLET: #{talep_id}",
                description=f"**Müşteri:** {kullanici.name} ({kullanici.id})",
                color=discord.Color.red()
            )
            yonetici_embed.add_field(name="Departman", value=self.departman, inline=True)
            yonetici_embed.add_field(name="Sipariş Numarası", value=self.siparis_no.value if self.siparis_no.value else 'Belirtilmedi', inline=True)
            yonetici_embed.add_field(name="Detaylı Sorun", value=self.detay.value, inline=False)
            
            # Detaylı raporu senin DM kutuna atıyoruz
            await yonetici.send(embed=yonetici_embed)
        except Exception as e:
            print(f"🚨 Yöneticiye bildirim gönderilirken bir hata oluştu: {e}")


class SSSDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Nasıl alışveriş yapabilirim?", value="alisveris", emoji="🛍️"),
            discord.SelectOption(label="Siparişimin durumunu nasıl öğrenebilirim?", value="durum", emoji="📦"),
            discord.SelectOption(label="Bir siparişi nasıl iptal edebilirim?", value="iptal", emoji="❌"),
            discord.SelectOption(label="Siparişim hasarlı gelirse ne yapmalıyım?", value="hasar", emoji="⚠️"),
            discord.SelectOption(label="Teknik destekle nasıl iletişime geçebilirim?", value="teknik", emoji="📞"),
            discord.SelectOption(label="Teslimat yöntemini değiştirebilir miyim?", value="teslimat", emoji="🚚")
        ]
        super().__init__(placeholder="Merak ettiğiniz bir konuyu buradan seçin...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        secilen = self.values[0]
        
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
        await interaction.response.send_message(embed=embed, ephemeral=True)


class DestekPaneliGörunumu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SSSDropdown())

    @discord.ui.button(label="💻 Programcı Desteği (Site / Ödeme)", style=discord.ButtonStyle.danger, row=1)
    async def programci_buton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DestekModali(departman="Programcılar"))

    @discord.ui.button(label="👟 Satış Departmanı (Ürün / Numara)", style=discord.ButtonStyle.success, row=1)
    async def satis_buton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DestekModali(departman="Satış Departmanı"))


# ==========================================
# 4. SÖZCÜK ANALİZİ VE METİN İŞLEME
# ==========================================
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    mesaj_kucuk = message.content.lower()

    if "hasarlı" in mesaj_kucuk or "yırtık" in mesaj_kucuk or "hasar" in mesaj_kucuk:
        embed = discord.Embed(
            title="⚠️ Hasarlı Ürün Yardımı",
            description="Mesajınızda hasarlı ürün ifadesi tespit edildi.\n\n**Çözüm:** Lütfen hemen müşteri hizmetlerimize hasar fotoğraflarını sağlayın. İade veya değişim sürecini başlatalım.\n\nDetaylı form açmak için lütfen `/yardim` komutunu kullanın.",
            color=discord.Color.orange()
        )
        await message.reply(embed=embed)
        return

    elif "iptal" in mesaj_kucuk and "sipariş" in mesaj_kucuk:
        embed = discord.Embed(
            title="❌ Sipariş İptal İşlemleri",
            description="**Çözüm:** Siparişiniz kargoya verilmeden önce iptal etmek istiyorsanız en kısa sürede bizimle iletişime geçmelisiniz.",
            color=discord.Color.orange()
        )
        await message.reply(embed=embed)
        return

    await bot.process_commands(message)


# ==========================================
# 5. EĞİK ÇİZGİ (SLASH) KOMUTLARI
# ==========================================
@bot.tree.command(name="yardim", description="Alabileceğin Her Şey teknik destek panelini açar.")
async def yardim_komutu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="👟 Alabileceğin Her Şey - Teknik Destek Merkezi",
        description="Mağazamıza hoş geldiniz! Sorunlarınızı hızlıca çözmek için aşağıdaki menüyü veya butonları kullanabilirsiniz.",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed, view=DestekPaneliGörunumu())


@bot.tree.command(name="talepler", description="[Yönetici] Bekleyen tüm açık destek biletlerini listeler.")
async def talepleri_listele(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    conn = sqlite3.connect('magaza_destek.db')
    c = conn.cursor()
    c.execute("SELECT id, kullanici_adi, departman, mesaj, tarih FROM talepler WHERE durum='Açık'")
    veriler = c.fetchall()
    conn.close()

    if not veriler:
        await interaction.followup.send("🎉 Şu anda çözüm bekleyen açık bir talep bulunmuyor!", ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 Aktif Müşteri Destek Talepleri",
        description="Aşağıdaki biletler uzman müdahalesi beklemektedir:",
        color=discord.Color.purple()
    )

    for bilet in veriler:
        bilet_id, k_adi, dept, msg, zaman = bilet
        embed.add_field(
            name=f"Bilet #{bilet_id} — Müşteri: {k_adi}",
            value=f"**Departman:** {dept}\n**Tarih:** {zaman}\n**İçerik:** {msg}\n" + "—"*15,
            inline=False
        )

    await interaction.followup.send(embed=embed, ephemeral=True)


@bot.tree.command(name="talep_kapat", description="[Yönetici] Talebi kapatır ve müşteriye otomatik DM gönderir.")
@app_commands.describe(bilet_id="Kapatılacak olan biletin benzersiz ID numarası")
async def talebi_kapat(interaction: discord.Interaction, bilet_id: int):
    await interaction.response.defer(ephemeral=True)

    conn = sqlite3.connect('magaza_destek.db')
    c = conn.cursor()
    c.execute("SELECT kullanici_id FROM talepler WHERE id=?", (bilet_id,))
    sonuc = c.fetchone()
    
    if not sonuc:
        await interaction.followup.send(f"❌ #{bilet_id} numaralı bir talep veri tabanında bulunamadı.", ephemeral=True)
        conn.close()
        return

    kullanici_id = sonuc[0]
    c.execute("UPDATE talepler SET durum='Kapalı' WHERE id=?", (bilet_id,))
    conn.commit()
    conn.close()

    dm_notu = "ve müşteriye bilgilendirme mesajı başarıyla iletildi."
    try:
        kullanici = await bot.fetch_user(int(kullanici_id))
        onay_embed = discord.Embed(
            title="👟 Alabileceğin Her Şey - Sipariş Güncellemesi",
            description=f"Merhaba, mağazamıza iletmiş olduğunuz **#{bilet_id}** numaralı destek talebiniz tamamlanmıştır.",
            color=discord.Color.blue()
        )
        onay_embed.add_field(
            name="🛠️ İşlem Detayı", 
            value="**Talebiniz gerçekleştirildi ve ayakkabınız onarıldı.** ✨", 
            inline=False
        )
        await kullanici.send(embed=onay_embed)
    except discord.Forbidden:
        dm_notu = "ancak DM kutusu kapalı olduğundan mesaj iletilemedi."
    except Exception as e:
        dm_notu = f"ancak DM gönderilirken bir sorun oluştu: {e}"

    await interaction.followup.send(f"✅ #{bilet_id} numaralı talep başarıyla kapatıldı {dm_notu}", ephemeral=True)


# ==========================================
# 6. BOT BAŞLATMA VE SENKRONİZASYON
# ==========================================
@bot.event
async def on_ready():
    print(f"--------------------------------------------------")
    print(f"🤖 Bot Aktif: {bot.user.name}")
    try:
        senkronize = await bot.tree.sync()
        print(f"🔄 {len(senkronize)} adet komut senkronize edildi.")
    except Exception as e:
        print(f"🚨 Senkronizasyon hatası: {e}")
    print(f"--------------------------------------------------")

if __name__ == "__main__":
    bot.run(config.TOKEN)
