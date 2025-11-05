"""
Gemini AI ile akıllı bildirim oluşturma servisi
Sadece haftalık öğrenci raporları için kullanılır
"""
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import AkilliBildirim, Ogrenci, EzberKaydi

# Gemini AI yapılandırması
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')


def gunluk_motivasyon_olustur():
    """Günlük kişisel motivasyon mesajı oluştur"""
    prompt = f"""
    Sen Şeyma'nın kişisel asistanısın. Bugün {datetime.now().strftime('%d %B %Y, %A')}. 
    Şeyma'ya günlük motivasyon mesajı yaz. Samimi, sıcak ve kişisel ol.
    Nasıl hissettiğini sor, günün nasıl geçtiğini merak et.
    Kısa ve öz tut (maksimum 3-4 cümle).
    
    Format:
    Başlık: [Kısa başlık]
    Mesaj: [Motivasyon mesajı]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Başlık ve mesajı ayır
        lines = text.strip().split('\n')
        baslik = lines[0].replace('Başlık:', '').strip()
        mesaj = '\n'.join(lines[1:]).replace('Mesaj:', '').strip()
        
        # Bildirimi oluştur
        bildirim = AkilliBildirim.objects.create(
            tur='GUNLUK',
            baslik=baslik,
            mesaj=mesaj
        )
        return bildirim
    except Exception as e:
        print(f"Gemini AI hatası: {e}")
        # Hata durumunda varsayılan mesaj
        return AkilliBildirim.objects.create(
            tur='GUNLUK',
            baslik='Günaydın Şeyma! 🌅',
            mesaj='Yeni bir gün, yeni fırsatlar! Bugün nasılsın? İyi misin? Umarım güzel bir gün geçiriyorsundur.'
        )


def haftalik_ogrenci_raporu():
    """Haftada 2 kez öğrenci analizi"""
    # Son 3-4 günün verilerini al
    baslangic = timezone.now() - timedelta(days=4)
    
    # En iyi öğrenciyi bul (en fazla ezber tamamlayan)
    ogrenciler = Ogrenci.objects.all()
    
    if not ogrenciler.exists():
        return None
    
    # Her öğrencinin son 4 gündeki performansını hesapla
    ogrenci_performans = []
    for ogr in ogrenciler:
        son_ezberler = EzberKaydi.objects.filter(
            ogrenci=ogr,
            durum='TAMAMLANDI',
            tamamlanma_tarihi__gte=baslangic
        ).count()
        ogrenci_performans.append({
            'ogrenci': ogr,
            'ezber_sayisi': son_ezberler
        })
    
    # Sırala
    ogrenci_performans.sort(key=lambda x: x['ezber_sayisi'], reverse=True)
    
    en_iyi = ogrenci_performans[0] if ogrenci_performans else None
    en_dusuk = ogrenci_performans[-1] if len(ogrenci_performans) > 1 else None
    
    # Gemini'ye rapor hazırlat
    prompt = f"""
    Sen Şeyma'nın öğretmenlik asistanısın. Son 4 günün öğrenci performans raporu:
    
    En İyi Öğrenci: {en_iyi['ogrenci'].ad_soyad if en_iyi else 'Yok'} 
    ({en_iyi['ezber_sayisi'] if en_iyi else 0} ezber tamamladı)
    
    {f"En Düşük Performans: {en_dusuk['ogrenci'].ad_soyad} ({en_dusuk['ezber_sayisi']} ezber)" if en_dusuk and en_dusuk['ezber_sayisi'] < en_iyi['ezber_sayisi'] else ''}
    
    Toplam Öğrenci: {ogrenciler.count()}
    
    Şeyma'ya kısa bir rapor hazırla:
    - En iyi öğrenciyi övüc bir şekilde belirt
    - Neden iyi performans gösterdiğini analiz et
    - Düşük performans gösterene uygulanabilir stratejiler öner
    - Sınıfın genel durumu hakkında yorum yap
    - Kısa ve öz tut (4-5 cümle)
    
    Format:
    Başlık: [Kısa başlık]
    Mesaj: [Rapor]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        lines = text.strip().split('\n')
        baslik = lines[0].replace('Başlık:', '').strip()
        mesaj = '\n'.join(lines[1:]).replace('Mesaj:', '').strip()
        
        bildirim = AkilliBildirim.objects.create(
            tur='OGRENCI',
            baslik=baslik,
            mesaj=mesaj,
            ilgili_ogrenci_id=en_iyi['ogrenci'].id if en_iyi else None
        )
        return bildirim
    except Exception as e:
        print(f"Gemini AI hatası: {e}")
        if en_iyi:
            return AkilliBildirim.objects.create(
                tur='OGRENCI',
                baslik='Haftalık Öğrenci Raporu 📊',
                mesaj=f'Son 4 günde {en_iyi["ogrenci"].ad_soyad} harika performans gösterdi! {en_iyi["ezber_sayisi"]} ezber tamamladı. Tebrikler!',
                ilgili_ogrenci_id=en_iyi['ogrenci'].id
            )
        return None


def haftalik_ezber_istatistigi():
    """Son haftanın ezber istatistikleri"""
    baslangic = timezone.now() - timedelta(days=7)
    
    tamamlanan = EzberKaydi.objects.filter(
        durum='TAMAMLANDI',
        tamamlanma_tarihi__gte=baslangic
    ).count()
    
    devam_eden = EzberKaydi.objects.filter(durum='DEVAM_EDIYOR').count()
    
    prompt = f"""
    Sen Şeyma'nın asistanısın. Son haftanın ezber istatistikleri:
    
    Tamamlanan Ezber: {tamamlanan}
    Devam Eden Ezber: {devam_eden}
    
    Bu istatistikler hakkında kısa ve motive edici bir yorum yaz.
    Başarıyı övüc bir şekilde belirt veya teşvik et.
    (2-3 cümle)
    
    Format:
    Başlık: [Kısa başlık]
    Mesaj: [Yorum]
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        lines = text.strip().split('\n')
        baslik = lines[0].replace('Başlık:', '').strip()
        mesaj = '\n'.join(lines[1:]).replace('Mesaj:', '').strip()
        
        bildirim = AkilliBildirim.objects.create(
            tur='EZBER',
            baslik=baslik,
            mesaj=mesaj
        )
        return bildirim
    except Exception as e:
        print(f"Gemini AI hatası: {e}")
        return AkilliBildirim.objects.create(
            tur='EZBER',
            baslik='Haftalık Ezber Raporu 📚',
            mesaj=f'Bu hafta {tamamlanan} ezber tamamlandı! {devam_eden} ezber ise devam ediyor. Harika bir performans!'
        )
