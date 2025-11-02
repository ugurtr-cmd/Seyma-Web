import google.generativeai as genai
from django.conf import settings
from .models import Ogrenci, SinavSonucu, EzberKaydi, ElifBaEzberDurumu
from django.db.models import Avg, Count, Q, Max
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)

class HaftalikRaporServisi:
    """Gemini AI destekli haftalık öğrenci durum raporu"""
    
    def __init__(self):
        api_key = getattr(settings, 'GOOGLE_AI_API_KEY', '')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            logger.warning("Google AI API key bulunamadı")
    
    def haftalik_istatistikleri_al(self):
        """Son 7 günün öğrenci istatistiklerini al"""
        bugun = date.today()
        bir_hafta_once = bugun - timedelta(days=7)
        
        # Toplam öğrenci sayısı
        toplam_ogrenci = Ogrenci.objects.count()
        
        # Son hafta eklenen öğrenciler
        yeni_ogrenciler = Ogrenci.objects.filter(
            kayit_tarihi__gte=bir_hafta_once
        ).count()
        
        # Sınav ortalamaları
        sinav_ortalamasi = SinavSonucu.objects.aggregate(
            ortalama=Avg('puan')
        )['ortalama'] or 0
        
        # En başarılı öğrenci
        en_basarili = Ogrenci.objects.annotate(
            ortalama_puan=Avg('sinavsonucu__puan')
        ).order_by('-ortalama_puan').first()
        
        # En düşük performanslı öğrenci
        en_dusuk = Ogrenci.objects.annotate(
            ortalama_puan=Avg('sinavsonucu__puan')
        ).order_by('ortalama_puan').first()
        
        # Ezber istatistikleri
        tamamlanan_ezberler = EzberKaydi.objects.filter(
            durum='TAMAMLANDI'
        ).count()
        
        devam_eden_ezberler = EzberKaydi.objects.filter(
            durum='DEVAM'
        ).count()
        
        # Elif Ba istatistikleri
        tamamlanan_elifba = ElifBaEzberDurumu.objects.filter(
            durum='TAMAMLANDI'
        ).count()
        
        # Seviye dağılımı
        seviye_dagilimi = {}
        for seviye_kod, seviye_ad in Ogrenci.SEVIYE_CHOICES:
            sayi = Ogrenci.objects.filter(seviye=seviye_kod).count()
            if sayi > 0:
                seviye_dagilimi[seviye_ad] = sayi
        
        return {
            'toplam_ogrenci': toplam_ogrenci,
            'yeni_ogrenciler': yeni_ogrenciler,
            'sinav_ortalamasi': round(sinav_ortalamasi, 1),
            'en_basarili': {
                'ad': en_basarili.ad_soyad if en_basarili else None,
                'ortalama': round(en_basarili.ortalama_puan or 0, 1) if en_basarili else 0
            },
            'en_dusuk': {
                'ad': en_dusuk.ad_soyad if en_dusuk else None,
                'ortalama': round(en_dusuk.ortalama_puan or 0, 1) if en_dusuk else 0
            },
            'tamamlanan_ezberler': tamamlanan_ezberler,
            'devam_eden_ezberler': devam_eden_ezberler,
            'tamamlanan_elifba': tamamlanan_elifba,
            'seviye_dagilimi': seviye_dagilimi
        }
    
    def gemini_rapor_olustur(self, istatistikler):
        """Gemini AI ile akıllı haftalık rapor oluştur"""
        if not self.model:
            return self.fallback_rapor_olustur(istatistikler)
        
        try:
            prompt = f"""
            Sen Şeyma için hafızlık eğitimi veren bir uzman öğretmensin. Aşağıdaki haftalık istatistiklere göre 
            kısa, öz ve motive edici bir rapor yaz. Raporun şeyma'ya hitap etsin ve samimi olsun.

            📊 HAFTALIK İSTATİSTİKLER:
            • Toplam öğrenci: {istatistikler['toplam_ogrenci']}
            • Bu hafta yeni öğrenci: {istatistikler['yeni_ogrenciler']}
            • Sınıf ortalaması: {istatistikler['sinav_ortalamasi']}
            • En başarılı öğrenci: {istatistikler['en_basarili']['ad']} ({istatistikler['en_basarili']['ortalama']} puan)
            • Gelişime ihtiyacı olan: {istatistikler['en_dusuk']['ad']} ({istatistikler['en_dusuk']['ortalama']} puan)
            • Tamamlanan ezberler: {istatistikler['tamamlanan_ezberler']}
            • Devam eden ezberler: {istatistikler['devam_eden_ezberler']}
            • Tamamlanan Elif Ba: {istatistikler['tamamlanan_elifba']}
            • Seviye dağılımı: {istatistikler['seviye_dagilimi']}

            RAPOR KURALLARI:
            1. Maksimum 150 kelime olsun
            2. Şeyma'ya doğrudan hitap et (Sen, senin, vs.)
            3. Olumlu ve motive edici ol
            4. Somut öneriler ver
            5. Emoji kullan ama abartma
            6. İslami bir dil kullan, dua cümleleri ekle

            Başlık kullanma, doğrudan raporu yaz:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini rapor oluşturma hatası: {e}")
            return self.fallback_rapor_olustur(istatistikler)
    
    def fallback_rapor_olustur(self, istatistikler):
        """Gemini çalışmazsa fallback rapor"""
        rapor = f"📊 Bu hafta {istatistikler['toplam_ogrenci']} öğrencin takip ediliyor. "
        
        if istatistikler['en_basarili']['ad']:
            rapor += f"En başarılı öğrencin {istatistikler['en_basarili']['ad']} "
            rapor += f"({istatistikler['en_basarili']['ortalama']} puan). "
        
        rapor += f"Sınıf ortalaması {istatistikler['sinav_ortalamasi']}. "
        
        if istatistikler['tamamlanan_ezberler'] > 0:
            rapor += f"{istatistikler['tamamlanan_ezberler']} ezber tamamlandı. "
        
        rapor += "Allah yolunda güzel çalışmalar! 🤲"
        
        return rapor
    
    def haftalik_rapor_olustur(self):
        """Tam haftalık rapor oluştur"""
        try:
            istatistikler = self.haftalik_istatistikleri_al()
            rapor_metni = self.gemini_rapor_olustur(istatistikler)
            
            return {
                'baslik': '📊 Haftalık Öğrenci Durum Raporu',
                'icerik': rapor_metni,
                'istatistikler': istatistikler,
                'tarih': date.today().strftime('%d.%m.%Y')
            }
            
        except Exception as e:
            logger.error(f"Haftalık rapor oluşturma hatası: {e}")
            return {
                'baslik': '📊 Haftalık Rapor',
                'icerik': 'Bu hafta öğrenci takibi devam ediyor. Allah kolaylık versin! 🤲',
                'istatistikler': {},
                'tarih': date.today().strftime('%d.%m.%Y')
            }

# Singleton instance
haftalik_rapor_servisi = HaftalikRaporServisi()