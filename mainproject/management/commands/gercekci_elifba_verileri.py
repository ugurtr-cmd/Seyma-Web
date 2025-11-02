from django.core.management.base import BaseCommand
from mainproject.models import Ogrenci, ElifBaEzberi, ElifBaEzberDurumu
from django.utils import timezone
import datetime
import random

class Command(BaseCommand):
    help = 'Tüm öğrenciler için gerçekçi Elif Ba ezber durumları oluşturur'

    def handle(self, *args, **options):
        ogrenciler = Ogrenci.objects.all()
        tum_elifbalar = ElifBaEzberi.objects.all().order_by('sira')
        
        self.stdout.write(f"{ogrenciler.count()} öğrenci için gerçekçi Elif Ba durumları oluşturuluyor...")
        
        for ogrenci in ogrenciler:
            # Her öğrenci için farklı seviyeler belirle
            kayit_suresi = (timezone.now().date() - ogrenci.kayit_tarihi).days
            
            # Kayıt süresine göre tamamlanan ezber sayısını belirle
            if kayit_suresi > 300:  # 10 aydan fazla
                tamamlanan_sayi = random.randint(10, 17)
                devam_eden_sayi = random.randint(0, 2)
            elif kayit_suresi > 180:  # 6 aydan fazla
                tamamlanan_sayi = random.randint(7, 12)
                devam_eden_sayi = random.randint(1, 3)
            elif kayit_suresi > 90:  # 3 aydan fazla
                tamamlanan_sayi = random.randint(4, 8)
                devam_eden_sayi = random.randint(1, 2)
            elif kayit_suresi > 30:  # 1 aydan fazla
                tamamlanan_sayi = random.randint(2, 5)
                devam_eden_sayi = random.randint(1, 2)
            else:  # Yeni kayıt
                tamamlanan_sayi = random.randint(0, 3)
                devam_eden_sayi = random.randint(0, 2)
            
            # İlk ezberlerden başlayarak tamamlananları işaretle
            for i, elifba in enumerate(tum_elifbalar[:tamamlanan_sayi]):
                gun_fark = random.randint(5, kayit_suresi) if kayit_suresi > 5 else random.randint(1, max(1, kayit_suresi))
                
                ElifBaEzberDurumu.objects.filter(
                    ogrenci=ogrenci,
                    ezber=elifba
                ).update(
                    durum='TAMAMLANDI',
                    baslama_tarihi=ogrenci.kayit_tarihi + datetime.timedelta(days=i*2),
                    bitis_tarihi=ogrenci.kayit_tarihi + datetime.timedelta(days=i*2 + random.randint(3, 10)),
                    tamamlandi_tarihi=ogrenci.kayit_tarihi + datetime.timedelta(days=i*2 + random.randint(3, 10)),
                    yorum=f'Seviye uygun, başarıyla tamamlandı'
                )
            
            # Devam eden ezberler
            devam_baslangic = tamamlanan_sayi
            for i, elifba in enumerate(tum_elifbalar[devam_baslangic:devam_baslangic+devam_eden_sayi]):
                ElifBaEzberDurumu.objects.filter(
                    ogrenci=ogrenci,
                    ezber=elifba
                ).update(
                    durum='DEVAM',
                    baslama_tarihi=timezone.now().date() - datetime.timedelta(days=random.randint(3, 15)),
                    yorum=f'Ezber devam ediyor, ilerleme kaydediliyor'
                )
            
            self.stdout.write(f"✓ {ogrenci.ad_soyad}: {tamamlanan_sayi} tamamlandı, {devam_eden_sayi} devam ediyor")
        
        # Genel istatistik
        total_tamamlanan = ElifBaEzberDurumu.objects.filter(durum='TAMAMLANDI').count()
        total_devam_eden = ElifBaEzberDurumu.objects.filter(durum='DEVAM').count()
        total_baslamayan = ElifBaEzberDurumu.objects.filter(durum='BASLAMADI').count()
        
        self.stdout.write("\n=== GENEL İSTATİSTİK ===")
        self.stdout.write(f"Toplam Tamamlanan: {total_tamamlanan}")
        self.stdout.write(f"Toplam Devam Eden: {total_devam_eden}")
        self.stdout.write(f"Toplam Başlamayan: {total_baslamayan}")
        
        # En başarılı 3 öğrenciyi göster
        self.stdout.write("\n=== EN BAŞARILI ÖĞRENCİLER ===")
        for ogrenci in ogrenciler:
            tamamlanan = ElifBaEzberDurumu.objects.filter(
                ogrenci=ogrenci,
                durum='TAMAMLANDI'
            ).count()
            ogrenci.tamamlanan_count = tamamlanan
        
        en_basarililar = sorted(ogrenciler, key=lambda x: x.tamamlanan_count, reverse=True)[:3]
        for i, ogrenci in enumerate(en_basarililar, 1):
            self.stdout.write(f"{i}. {ogrenci.ad_soyad}: {ogrenci.tamamlanan_count} ezber tamamladı")
        
        self.stdout.write(self.style.SUCCESS('\nGerçekçi Elif Ba verileri oluşturuldu!'))