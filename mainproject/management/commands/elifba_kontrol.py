from django.core.management.base import BaseCommand
from mainproject.models import ElifBaEzberi, ElifBaEzberDurumu, Ogrenci

class Command(BaseCommand):
    help = 'Elif Ba ezberlerini kontrol eder ve eksik olanları oluşturur'

    def handle(self, *args, **options):
        # Mevcut Elif Ba ezberlerini kontrol et
        mevcut_elifba_sayisi = ElifBaEzberi.objects.count()
        self.stdout.write(f"Mevcut Elif Ba ezber sayısı: {mevcut_elifba_sayisi}")
        
        if mevcut_elifba_sayisi == 0:
            self.stdout.write("Elif Ba ezberleri oluşturuluyor...")
            # Elif Ba ezberlerini oluştur
            ezberler = [
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
            
            for sira, ad in ezberler:
                ezber, created = ElifBaEzberi.objects.get_or_create(
                    sira=sira,
                    defaults={'ad': ad, 'tahmini_sure': 3}
                )
                if created:
                    self.stdout.write(f"✓ {ad} oluşturuldu")
        
        # Mevcut öğrenciler için Elif Ba durumları oluştur
        ogrenciler = Ogrenci.objects.all()
        tum_elifbalar = ElifBaEzberi.objects.all()
        
        self.stdout.write(f"\n{ogrenciler.count()} öğrenci için Elif Ba durumları kontrol ediliyor...")
        
        for ogrenci in ogrenciler:
            for elifba in tum_elifbalar:
                durum, created = ElifBaEzberDurumu.objects.get_or_create(
                    ogrenci=ogrenci,
                    ezber=elifba,
                    defaults={'durum': 'BASLAMADI'}
                )
                if created:
                    self.stdout.write(f"✓ {ogrenci.ad_soyad} - {elifba.ad} durumu oluşturuldu")
        
        # Son durum raporu
        self.stdout.write("\n=== SON DURUM ===")
        self.stdout.write(f"Toplam Elif Ba ezber sayısı: {ElifBaEzberi.objects.count()}")
        self.stdout.write(f"Toplam öğrenci sayısı: {Ogrenci.objects.count()}")
        self.stdout.write(f"Toplam Elif Ba durum kayıtları: {ElifBaEzberDurumu.objects.count()}")
        
        # Örnek öğrenci analizi
        if ogrenciler.exists():
            ornek_ogrenci = ogrenciler.first()
            tamamlanan = ElifBaEzberDurumu.objects.filter(
                ogrenci=ornek_ogrenci,
                durum='TAMAMLANDI'
            ).count()
            self.stdout.write(f"\nÖrnek: {ornek_ogrenci.ad_soyad} - Tamamlanan Elif Ba: {tamamlanan}")
        
        self.stdout.write(self.style.SUCCESS('\nElif Ba kontrol işlemi tamamlandı!'))