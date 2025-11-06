from django.db import models
from django.utils import timezone

class Ogrenci(models.Model):
    SEVIYE_CHOICES = [
        ('HAZ1', 'Hazırlık 1. Seviye'),
        ('HAZ2', 'Hazırlık 2. Seviye'),
        ('HAZ3', 'Hazırlık 3. Seviye'),
        ('TEMEL', 'Temel Hafızlık'),
        ('ILERI', 'İleri Hafızlık'),
    ]
    
    ad_soyad = models.CharField(max_length=100)
    kayit_tarihi = models.DateField(default=timezone.now)
    seviye = models.CharField(max_length=5, choices=SEVIYE_CHOICES, default='HAZ1')
    profil_foto = models.ImageField(upload_to='ogrenci_profil/', blank=True, null=True)
    ozel_notlar = models.TextField(blank=True)
    son_guncelleme = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Öğrenciler"
    
    def __str__(self):
        return self.ad_soyad
    
    def tamamlanan_ezber_sayisi(self):
        return self.ezberkaydi_set.filter(durum='TAMAMLANDI').count()  # Bu satırı düzelt
    
    def ortalama_ders_notu(self):
        from django.db.models import Avg
        ortalama = self.dersnotu_set.aggregate(Avg('not_degeri'))['not_degeri__avg']
        return round(ortalama, 2) if ortalama else 0
        
    def tamamlanan_elifba_sayisi(self):
        return self.elifbaezberdurumu_set.filter(durum='TAMAMLANDI').count()

    
class ElifBaEzberi(models.Model):
    EZBER_SIRASI = [
        (1, '1. Fatiha Suresi'),
        (2, '2. Bakara 1-5'),
        (3, '3. Rabbena Duaları'),
        (4, '4. Ezan Duası'),
        (5, '5. Kamet'),
        (6, '6. Tesbihat'),
        (7, '7. Amentü Duası'),
        (8, '8. İftitah Duası'),
        (9, '9. Tahiyyat Duası'),
        (10, '10. Salli-barik Duaları'),
        (11, '11. Kunut Duası'),
        (12, '12. Yemek Duası'),
        (13, '13. Başlangıç Duası'),
        (14, '14. İstiğfar Duası'),
        (15, '15. Ayetel Kürsi'),
        (16, '16. Amenerrasülü'),
        (17, '17. La yestevi'),
    ]
    
    ad = models.CharField(max_length=100)
    sira = models.PositiveSmallIntegerField(choices=EZBER_SIRASI, unique=True)
    tahmini_sure = models.PositiveSmallIntegerField(help_text="Tahmini ezber süresi (gün)", default=3)
    aciklama = models.TextField(blank=True)
    
    class Meta:
        ordering = ['sira']
        verbose_name = "Elif Ba Ezberi"
        verbose_name_plural = "Elif Ba Ezberleri"
    
    def __str__(self):
        return f"{self.get_sira_display()} - {self.ad}"

class ElifBaEzberDurumu(models.Model):
    DURUM_SECENEKLERI = [
        ('BASLAMADI', 'Başlamadı'),
        ('DEVAM', 'Devam Ediyor'),
        ('TAMAMLANDI', 'Tamamlandı'),
    ]
    
    ogrenci = models.ForeignKey(Ogrenci, on_delete=models.CASCADE)
    ezber = models.ForeignKey(ElifBaEzberi, on_delete=models.CASCADE)
    durum = models.CharField(max_length=10, choices=DURUM_SECENEKLERI, default='BASLAMADI')
    baslama_tarihi = models.DateField(null=True, blank=True)
    bitis_tarihi = models.DateField(null=True, blank=True)
    yorum = models.TextField(blank=True)
    tamamlandi_tarihi = models.DateField(null=True, blank=True, verbose_name="Tamamlanma Tarihi")
    

    class Meta:
        unique_together = ['ogrenci', 'ezber']
        verbose_name = "Elif Ba Ezber Durumu"
        verbose_name_plural = "Elif Ba Ezber Durumları"
    
    def __str__(self):
        return f"{self.ogrenci} - {self.ezber}"
    
    def save(self, *args, **kwargs):
        if self.durum == 'TAMAMLANDI' and not self.tamamlandi_tarihi:
            self.tamamlandi_tarihi = timezone.now().date()
        super().save(*args, **kwargs)

class Ders(models.Model):
    DERS_TURU = [
        ('AKAID', 'Akaid (İtikad)'),
        ('FIKIH', 'Fıkıh (İbadet)'),
        ('SIYER', 'Siyer'),
        ('TECV', 'Tecvid'),
    ]
    
    ad = models.CharField(max_length=100)
    tur = models.CharField(max_length=5, choices=DERS_TURU, unique=True)
    aciklama = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Dersler"
    
    def __str__(self):
        return self.get_tur_display()
    
    def save(self, *args, **kwargs):
        if not self.ad:
            self.ad = self.get_tur_display()
        super().save(*args, **kwargs)

class EzberSuresi(models.Model):
    EZBER_SIRASI = [
    (1, '1. 30. Cüz Tamamı'),
    (2, '2. Mülk Suresi'),
    (3, '3. Cin Suresi'),
    (4, '4. Kıyame Suresi'),
    (5, '5. Cuma Suresi'),
    (6, '6. Saff Suresi'),
    (7, '7. Rahman Suresi'),
    (8, '8. Vakia Suresi'),
    (9, '9. Fetih Suresi'),
    (10, '10. Hucurat Suresi'),
    (11, '11. Yasin Suresi'),
    (12, '12. Enfal Suresi'),
    (13, '13. İsra Suresi'),
    ]

    ad = models.CharField(max_length=100)
    sira = models.PositiveSmallIntegerField(choices=EZBER_SIRASI, unique=True)
    tahmini_sure = models.PositiveSmallIntegerField(help_text="Tahmini ezber süresi (gün)", default=7)
    aciklama = models.TextField(blank=True)
    
    class Meta:
        ordering = ['sira']
        verbose_name = "Ezber Süresi"
        verbose_name_plural = "Ezber Süreleri"
    
    def __str__(self):
        return f"{self.get_sira_display()} - {self.ad}"


# models.py - Mevcut modellere ekle


class Alinti(models.Model):
    quote_text = models.TextField(verbose_name="Alıntı Metni")
    author = models.CharField(max_length=200, blank=True, null=True, verbose_name="Yazar")
    source = models.CharField(max_length=300, blank=True, null=True, verbose_name="Kaynak")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kategori")
    isActive = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    def __str__(self):
        return self.quote_text[:50] + "..." if len(self.quote_text) > 50 else self.quote_text

    class Meta:
        verbose_name = "Alıntı"
        verbose_name_plural = "Alıntılar"

class DersNotu(models.Model):
    ogrenci = models.ForeignKey(Ogrenci, on_delete=models.CASCADE)
    ders = models.ForeignKey(Ders, on_delete=models.CASCADE)
    not_degeri = models.PositiveSmallIntegerField(default=0)  # 0-100 arası
    yorum = models.TextField(blank=True)
    tarih = models.DateField(default=timezone.now)  # Yeni tarih alanı
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['ogrenci', 'ders', 'tarih']  # Benzersizlik kısıtını güncelle
        verbose_name = "Ders Notu"
        verbose_name_plural = "Ders Notları"
    
    def __str__(self):
        return f"{self.ogrenci} - {self.ders}: {self.not_degeri} ({self.tarih})"

class SinavSonucu(models.Model):
    SINAV_TIPLERI = [
        ('VIZE', 'Vize Sınavı'),
        ('FINAL', 'Final Sınavı'),
        ('QUIZ', 'Quiz'),
        ('PROJE', 'Proje'),
        ('SOZLU', 'Sözlü Sınavı'),
    ]
    
    ogrenci = models.ForeignKey(Ogrenci, on_delete=models.CASCADE)
    ders = models.ForeignKey(Ders, on_delete=models.CASCADE)
    sinav_tipi = models.CharField(max_length=10, choices=SINAV_TIPLERI)
    puan = models.PositiveSmallIntegerField()  # 0-100 arası
    tarih = models.DateField(default=timezone.now)
    aciklama = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Sınav Sonucu"
        verbose_name_plural = "Sınav Sonuçları"
    
    def __str__(self):
        return f"{self.ogrenci} - {self.ders} {self.get_sinav_tipi_display()}: {self.puan}"

class EzberKaydi(models.Model):
    ZORLUK_SEVIYELERI = [
        (1, 'Kolay'),
        (2, 'Orta'),
        (3, 'Zor'),
    ]
    
    DURUM_SECENEKLERI = [
        ('BASLAMADI', 'Başlamadı'),
        ('DEVAM', 'Devam Ediyor'),
        ('TAMAMLANDI', 'Tamamlandı'),
    ]
    
    ogrenci = models.ForeignKey(Ogrenci, on_delete=models.CASCADE)
    sure = models.ForeignKey(EzberSuresi, on_delete=models.CASCADE)
    durum = models.CharField(max_length=10, choices=DURUM_SECENEKLERI, default='BASLAMADI')
    baslama_tarihi = models.DateField(null=True, blank=True)
    bitis_tarihi = models.DateField(null=True, blank=True)
    tahmini_bitis = models.DateField(null=True, blank=True)
    gunluk_calisma = models.PositiveSmallIntegerField(default=1, help_text="Günlük çalışma saati")
    zorluk = models.PositiveSmallIntegerField(choices=ZORLUK_SEVIYELERI, default=2)
    yorum = models.TextField(blank=True)
    ilerleme = models.IntegerField(default=0, verbose_name="İlerleme Yüzdesi")

    class Meta:
        unique_together = ['ogrenci', 'sure']
        verbose_name = "Ezber Kaydı"
        verbose_name_plural = "Ezber Kayıtları"
    
    def __str__(self):
        return f"{self.ogrenci} - {self.sure}"
    
    def save(self, *args, **kwargs):
        if self.durum == 'DEVAM' and not self.baslama_tarihi:
            self.baslama_tarihi = timezone.now().date()
        elif self.durum == 'TAMAMLANDI' and not self.bitis_tarihi:
            self.bitis_tarihi = timezone.now().date()
        super().save(*args, **kwargs)


class GunlukMesaj(models.Model):
    """Şeyma için günlük kişisel motivasyon mesajları"""
    MESAJ_TIPLERI = [
        ('GUNAYDIN', 'Günaydın Mesajı'),
        ('MOTIVASYON', 'Motivasyon Mesajı'),
        ('DINI', 'Dini İçerik'),
        ('EGITIM', 'Eğitim Tavsiyesi'),
        ('KISISEL', 'Kişisel Gelişim'),
        ('DUYGU', 'Duygusal Destek'),
        ('BASARI', 'Başarı Hikayeleri'),
        ('DIGER', 'Diğer'),
    ]
    
    tarih = models.DateField(default=timezone.now, unique=True)
    mesaj = models.TextField()
    mesaj_tipi = models.CharField(max_length=10, choices=MESAJ_TIPLERI, default='MOTIVASYON')
    okundu = models.BooleanField(default=False)
    begeni = models.BooleanField(default=False, verbose_name="Beğendi mi?")
    not_puani = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-10 arası puan")
    ek_notlar = models.TextField(blank=True, verbose_name="Şeyma'nın Notları")
    
    # AI ile oluşturulma bilgileri
    ai_generated = models.BooleanField(default=True)
    ai_prompt = models.TextField(blank=True, verbose_name="Kullanılan AI Prompt")
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Günlük Mesaj"
        verbose_name_plural = "Günlük Mesajlar"
        ordering = ['-tarih']
    
    def __str__(self):
        return f"{self.tarih.strftime('%d/%m/%Y')} - {self.get_mesaj_tipi_display()}"
    
    def mesaj_ozeti(self):
        """Mesajın ilk 50 karakteri"""
        return self.mesaj[:50] + "..." if len(self.mesaj) > 50 else self.mesaj
    
    @classmethod
    def bugunun_mesaji(cls):
        """Bugünün mesajını getir, yoksa oluştur"""
        bugun = timezone.now().date()
        try:
            return cls.objects.get(tarih=bugun)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def gecmis_mesajlar(cls, gun_sayisi=7):
        """Son N günün mesajlarını getir"""
        bugun = timezone.now().date()
        baslangic = bugun - timezone.timedelta(days=gun_sayisi)
        return cls.objects.filter(tarih__gte=baslangic).order_by('-tarih')


class BildirimAbonelik(models.Model):
    """Web bildirim abonelik bilgileri"""
    endpoint = models.TextField(unique=True)
    p256dh_key = models.TextField()
    auth_key = models.TextField()
    aktif = models.BooleanField(default=True)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Bildirim Aboneliği"
        verbose_name_plural = "Bildirim Abonelikleri"
    
    def __str__(self):
        return f"Abonelik {self.id} - {self.olusturulma_tarihi.strftime('%d.%m.%Y')}"


class BildirimGecmisi(models.Model):
    """Gönderilen bildirimler geçmişi"""
    BILDIRIM_TIPLERI = [
        ('GUNLUK_MESAJ', 'Günlük Kişisel Mesaj'),
        ('HAFTALIK_RAPOR', 'Haftalık Öğrenci Raporu'),
        ('SISTEM', 'Sistem Bildirimi'),
        ('HOSGELDIN', 'Hoş Geldin Mesajı'),
    ]
    
    tip = models.CharField(max_length=20, choices=BILDIRIM_TIPLERI)
    baslik = models.CharField(max_length=200)
    icerik = models.TextField()
    gonderilme_tarihi = models.DateTimeField(auto_now_add=True)
    basarili_gonderim = models.PositiveIntegerField(default=0)
    basarisiz_gonderim = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Bildirim Geçmişi"
        verbose_name_plural = "Bildirim Geçmişleri"
        ordering = ['-gonderilme_tarihi']
    
    def __str__(self):
        return f"{self.get_tip_display()} - {self.baslik[:50]}..."


class KonusmaOturumu(models.Model):
    """Kullanıcıların Şeyma'ya Sor ile yaptığı sohbet oturumları"""
    kullanici = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='konusma_oturumlari')
    baslik = models.CharField(max_length=200, blank=True)  # İlk sorudan otomatik oluşturulacak
    baslama_zamani = models.DateTimeField(auto_now_add=True)
    son_mesaj_zamani = models.DateTimeField(auto_now=True)
    aktif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Konuşma Oturumu"
        verbose_name_plural = "Konuşma Oturumları"
        ordering = ['-son_mesaj_zamani']
    
    def __str__(self):
        return f"{self.kullanici.username} - {self.baslik[:50] if self.baslik else 'Yeni Sohbet'}"
    
    def mesaj_sayisi(self):
        return self.mesajlar.count()


class KonusmaMesaji(models.Model):
    """Sohbet geçmişindeki her bir mesaj"""
    MESAJ_TIPI = [
        ('USER', 'Kullanıcı'),
        ('AI', 'Şeyma (AI)'),
    ]
    
    oturum = models.ForeignKey(KonusmaOturumu, on_delete=models.CASCADE, related_name='mesajlar')
    tip = models.CharField(max_length=4, choices=MESAJ_TIPI)
    icerik = models.TextField()
    zaman = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Konuşma Mesajı"
        verbose_name_plural = "Konuşma Mesajları"
        ordering = ['zaman']
    
    def __str__(self):
        return f"{self.get_tip_display()} - {self.icerik[:30]}..."


class AkilliBildirim(models.Model):
    """Gemini AI tarafından oluşturulan kişiselleştirilmiş bildirimler"""
    BILDIRIM_TURU = [
        ('GUNLUK', 'Günlük Motivasyon'),
        ('YAZI', 'Yazı Analizi'),
        ('ALINTI', 'Alıntı Yorumu'),
        ('OGRENCI', 'Öğrenci Raporu'),
        ('EZBER', 'Ezber İstatistikleri'),
    ]
    
    tur = models.CharField(max_length=10, choices=BILDIRIM_TURU)
    baslik = models.CharField(max_length=200)
    mesaj = models.TextField()
    olusturma_zamani = models.DateTimeField(auto_now_add=True)
    okundu = models.BooleanField(default=False)
    ilgili_yazi_id = models.IntegerField(null=True, blank=True)
    ilgili_alinti_id = models.IntegerField(null=True, blank=True)
    ilgili_ogrenci_id = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Akıllı Bildirim"
        verbose_name_plural = "Akıllı Bildirimler"
        ordering = ['-olusturma_zamani']
    
    def __str__(self):
        return f"{self.get_tur_display()} - {self.baslik[:50]}"
    
    def okundu_olarak_isaretle(self):
        self.okundu = True
        self.save()


class Galeri(models.Model):
    """Depolama alanına kaydedilen fotoğraflar için galeri sistemi"""
    KATEGORI_CHOICES = [
        ('YAZI', 'Yazı Fotoğrafı'),
        ('MANUEL', 'Manuel Yükleme'),
        ('OGRENCI', 'Öğrenci Profil'),
        ('GENEL', 'Genel'),
    ]
    
    baslik = models.CharField(max_length=200, help_text="Fotoğraf başlığı")
    aciklama = models.TextField(blank=True, help_text="Fotoğraf açıklaması")
    dosya = models.ImageField(upload_to='galeri/%Y/%m/', help_text="Fotoğraf dosyası")
    kategori = models.CharField(max_length=10, choices=KATEGORI_CHOICES, default='GENEL')
    yukleme_tarihi = models.DateTimeField(auto_now_add=True)
    dosya_boyutu = models.PositiveIntegerField(null=True, blank=True, help_text="KB cinsinden boyut")
    genislik = models.PositiveIntegerField(null=True, blank=True)
    yukseklik = models.PositiveIntegerField(null=True, blank=True)
    ilgili_yazi_id = models.PositiveIntegerField(null=True, blank=True, help_text="Hangi yazıya ait")
    
    class Meta:
        verbose_name = "Galeri Fotoğrafı"
        verbose_name_plural = "Galeri Fotoğrafları"
        ordering = ['-yukleme_tarihi']
    
    def __str__(self):
        return f"{self.baslik} ({self.get_kategori_display()})"
    
    def dosya_boyutu_mb(self):
        """Dosya boyutunu MB olarak döndür"""
        if self.dosya_boyutu:
            return round(self.dosya_boyutu / 1024, 2)
        return 0
    
    def save(self, *args, **kwargs):
        """Dosya boyutunu otomatik hesapla"""
        if self.dosya:
            try:
                # Dosya boyutunu KB olarak kaydet
                self.dosya_boyutu = self.dosya.size // 1024
                
                # Resim boyutlarını al
                from PIL import Image
                image = Image.open(self.dosya)
                self.genislik, self.yukseklik = image.size
            except:
                pass
        
        super().save(*args, **kwargs)
