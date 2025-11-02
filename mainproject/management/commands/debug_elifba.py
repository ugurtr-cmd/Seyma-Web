from django.core.management.base import BaseCommand
from mainproject.models import Ogrenci, ElifBaEzberDurumu
from django.db.models import Q, Count

class Command(BaseCommand):
    help = 'Elif Ba istatistiklerini debug eder'

    def handle(self, *args, **options):
        ogrenci = Ogrenci.objects.get(id=112)  # Hicret Kurt
        
        self.stdout.write(f"=== {ogrenci.ad_soyad} DEBUG ===")
        
        # İlişkili QuerySet'i al
        elifba_durumlari = ogrenci.elifbaezberdurumu_set.all()
        self.stdout.write(f"QuerySet count: {elifba_durumlari.count()}")
        
        # Aggregate ile hesaplama
        elifba_durumlari_istatistik = elifba_durumlari.aggregate(
            tamamlanan=Count('id', filter=Q(durum='TAMAMLANDI')),
            devam_eden=Count('id', filter=Q(durum='DEVAM')),
            baslamayan=Count('id', filter=Q(durum='BASLAMADI'))
        )
        self.stdout.write(f"Aggregate sonucu: {elifba_durumlari_istatistik}")
        
        # Manual hesaplama
        manual_tamamlanan = elifba_durumlari.filter(durum='TAMAMLANDI').count()
        manual_devam_eden = elifba_durumlari.filter(durum='DEVAM').count()
        manual_baslamayan = elifba_durumlari.filter(durum='BASLAMADI').count()
        
        self.stdout.write(f"Manual hesaplama:")
        self.stdout.write(f"  Tamamlanan: {manual_tamamlanan}")
        self.stdout.write(f"  Devam Eden: {manual_devam_eden}")
        self.stdout.write(f"  Başlamayan: {manual_baslamayan}")
        
        # Prefetch ile test
        from django.db.models import Prefetch
        ogrenci_prefetch = Ogrenci.objects.prefetch_related(
            Prefetch('elifbaezberdurumu_set', queryset=ElifBaEzberDurumu.objects.select_related('ezber'))
        ).get(id=112)
        
        elifba_prefetch = ogrenci_prefetch.elifbaezberdurumu_set.all()
        self.stdout.write(f"Prefetch QuerySet count: {elifba_prefetch.count()}")
        
        prefetch_istatistik = elifba_prefetch.aggregate(
            tamamlanan=Count('id', filter=Q(durum='TAMAMLANDI')),
            devam_eden=Count('id', filter=Q(durum='DEVAM')),
            baslamayan=Count('id', filter=Q(durum='BASLAMADI'))
        )
        self.stdout.write(f"Prefetch aggregate: {prefetch_istatistik}")
        
        self.stdout.write(self.style.SUCCESS('Debug tamamlandı!'))