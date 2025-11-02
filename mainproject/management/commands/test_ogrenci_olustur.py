from django.core.management.base import BaseCommand
from mainproject.models import Ogrenci, ElifBaEzberi, ElifBaEzberDurumu
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Test öğrencisi oluşturur ve Elif Ba ezberlerini test eder'

    def handle(self, *args, **options):
        # Test öğrencisi oluştur
        test_ogrenci, created = Ogrenci.objects.get_or_create(
            ad_soyad="Test Öğrenci",
            defaults={
                'seviye': 'HAZ2',
                'kayit_tarihi': timezone.now().date() - datetime.timedelta(days=60),
                'ozel_notlar': 'Test amaçlı oluşturulmuş öğrenci'
            }
        )
        
        if created:
            self.stdout.write("✓ Test öğrencisi oluşturuldu")
        else:
            self.stdout.write("• Test öğrencisi zaten var")
        
        # Elif Ba ezberleri için durum kayıtları oluştur
        tum_elifbalar = ElifBaEzberi.objects.all()
        self.stdout.write(f"Toplam Elif Ba ezber sayısı: {tum_elifbalar.count()}")
        
        # İlk 5 Elif Ba ezberini tamamlanmış olarak işaretle
        for i, elifba in enumerate(tum_elifbalar[:5], 1):
            durum, created = ElifBaEzberDurumu.objects.get_or_create(
                ogrenci=test_ogrenci,
                ezber=elifba,
                defaults={
                    'durum': 'TAMAMLANDI',
                    'baslama_tarihi': timezone.now().date() - datetime.timedelta(days=50-i*3),
                    'bitis_tarihi': timezone.now().date() - datetime.timedelta(days=45-i*3),
                    'tamamlandi_tarihi': timezone.now().date() - datetime.timedelta(days=45-i*3),
                    'yorum': f'Test için {i}. ezber tamamlandı'
                }
            )
            if created:
                self.stdout.write(f"✓ {elifba.ad} tamamlandı olarak işaretlendi")
        
        # 2 tane devam eden ezber ekle
        for i, elifba in enumerate(tum_elifbalar[5:7], 6):
            durum, created = ElifBaEzberDurumu.objects.get_or_create(
                ogrenci=test_ogrenci,
                ezber=elifba,
                defaults={
                    'durum': 'DEVAM',
                    'baslama_tarihi': timezone.now().date() - datetime.timedelta(days=10),
                    'yorum': f'Test için {i}. ezber devam ediyor'
                }
            )
            if created:
                self.stdout.write(f"✓ {elifba.ad} devam ediyor olarak işaretlendi")
        
        # Kalan ezberleri başlamadı olarak bırak
        for elifba in tum_elifbalar[7:]:
            durum, created = ElifBaEzberDurumu.objects.get_or_create(
                ogrenci=test_ogrenci,
                ezber=elifba,
                defaults={'durum': 'BASLAMADI'}
            )
        
        # İstatistikleri göster
        tamamlanan = ElifBaEzberDurumu.objects.filter(
            ogrenci=test_ogrenci,
            durum='TAMAMLANDI'
        ).count()
        
        devam_eden = ElifBaEzberDurumu.objects.filter(
            ogrenci=test_ogrenci,
            durum='DEVAM'
        ).count()
        
        baslamayan = ElifBaEzberDurumu.objects.filter(
            ogrenci=test_ogrenci,
            durum='BASLAMADI'
        ).count()
        
        self.stdout.write("\n=== TEST ÖĞRENCİSİ ELİF BA DURUMU ===")
        self.stdout.write(f"Öğrenci: {test_ogrenci.ad_soyad}")
        self.stdout.write(f"Tamamlanan: {tamamlanan}")
        self.stdout.write(f"Devam Eden: {devam_eden}")
        self.stdout.write(f"Başlamayan: {baslamayan}")
        self.stdout.write(f"Toplam: {tamamlanan + devam_eden + baslamayan}")
        
        # Tamamlanan ezberleri listele
        tamamlananlar = ElifBaEzberDurumu.objects.filter(
            ogrenci=test_ogrenci,
            durum='TAMAMLANDI'
        ).select_related('ezber').order_by('ezber__sira')
        
        self.stdout.write("\n=== TAMAMLANAN ELİF BA EZBERLERİ ===")
        for durum in tamamlananlar:
            self.stdout.write(f"{durum.ezber.sira}. {durum.ezber.ad}")
        
        self.stdout.write(f"\nTest öğrencisi ID: {test_ogrenci.id}")
        self.stdout.write("AI analizi için bu öğrenciyi kullanabilirsiniz!")
        self.stdout.write(self.style.SUCCESS('\nTest verisi oluşturma tamamlandı!'))