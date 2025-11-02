from django.core.management.base import BaseCommand
from mainproject.models import Ogrenci, ElifBaEzberDurumu, ElifBaEzberi

class Command(BaseCommand):
    help = 'Belirli bir öğrencinin Elif Ba ezber detaylarını gösterir'

    def add_arguments(self, parser):
        parser.add_argument('--ogrenci-id', type=int, help='Öğrenci ID si')
        parser.add_argument('--ad-soyad', type=str, help='Öğrenci adı soyadı')

    def handle(self, *args, **options):
        ogrenci_id = options.get('ogrenci_id')
        ad_soyad = options.get('ad_soyad')
        
        if ogrenci_id:
            try:
                ogrenci = Ogrenci.objects.get(id=ogrenci_id)
            except Ogrenci.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"ID {ogrenci_id} ile öğrenci bulunamadı"))
                return
        elif ad_soyad:
            try:
                ogrenci = Ogrenci.objects.get(ad_soyad__icontains=ad_soyad)
            except Ogrenci.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"'{ad_soyad}' adında öğrenci bulunamadı"))
                return
            except Ogrenci.MultipleObjectsReturned:
                ogrenciler = Ogrenci.objects.filter(ad_soyad__icontains=ad_soyad)
                self.stdout.write("Birden fazla öğrenci bulundu:")
                for ogr in ogrenciler:
                    self.stdout.write(f"ID: {ogr.id} - {ogr.ad_soyad}")
                return
        else:
            # İlk öğrenciyi al
            ogrenci = Ogrenci.objects.first()
            if not ogrenci:
                self.stdout.write(self.style.ERROR("Hiç öğrenci bulunamadı"))
                return
        
        self.stdout.write(f"\n=== {ogrenci.ad_soyad} - ELİF BA EZBER DETAYLARI ===")
        self.stdout.write(f"Öğrenci ID: {ogrenci.id}")
        self.stdout.write(f"Seviye: {ogrenci.get_seviye_display()}")
        self.stdout.write(f"Kayıt Tarihi: {ogrenci.kayit_tarihi}")
        
        # Elif Ba durumlarını al
        elifba_durumlari = ElifBaEzberDurumu.objects.filter(
            ogrenci=ogrenci
        ).select_related('ezber').order_by('ezber__sira')
        
        # İstatistikler
        tamamlanan = elifba_durumlari.filter(durum='TAMAMLANDI').count()
        devam_eden = elifba_durumlari.filter(durum='DEVAM').count()
        baslamayan = elifba_durumlari.filter(durum='BASLAMADI').count()
        
        self.stdout.write(f"\nTamamlanan: {tamamlanan}")
        self.stdout.write(f"Devam Eden: {devam_eden}")
        self.stdout.write(f"Başlamayan: {baslamayan}")
        self.stdout.write(f"Toplam: {tamamlanan + devam_eden + baslamayan}")
        
        # Tamamlanan ezberler
        self.stdout.write("\n=== TAMAMLANAN ELİF BA EZBERLERİ ===")
        tamamlananlar = elifba_durumlari.filter(durum='TAMAMLANDI')
        if tamamlananlar:
            for durum in tamamlananlar:
                tarih_str = durum.tamamlandi_tarihi.strftime('%d/%m/%Y') if durum.tamamlandi_tarihi else 'Tarih yok'
                self.stdout.write(f"✓ {durum.ezber.sira}. {durum.ezber.ad} ({tarih_str})")
        else:
            self.stdout.write("Tamamlanan ezber yok")
        
        # Devam eden ezberler
        self.stdout.write("\n=== DEVAM EDEN ELİF BA EZBERLERİ ===")
        devam_edenler = elifba_durumlari.filter(durum='DEVAM')
        if devam_edenler:
            for durum in devam_edenler:
                baslama_str = durum.baslama_tarihi.strftime('%d/%m/%Y') if durum.baslama_tarihi else 'Tarih yok'
                self.stdout.write(f"🔄 {durum.ezber.sira}. {durum.ezber.ad} (Başlangıç: {baslama_str})")
        else:
            self.stdout.write("Devam eden ezber yok")
        
        # AI analizi için veri formatı
        self.stdout.write("\n=== AI ANALİZİ İÇİN VERİ FORMATI ===")
        
        elifba_detay_listesi = []
        for durum in elifba_durumlari:
            elifba_detay_listesi.append({
                'sira': durum.ezber.sira,
                'ad': durum.ezber.ad,
                'durum': durum.get_durum_display(),
                'baslama_tarihi': durum.baslama_tarihi.strftime('%d/%m/%Y') if durum.baslama_tarihi else None,
                'bitis_tarihi': durum.bitis_tarihi.strftime('%d/%m/%Y') if durum.bitis_tarihi else None,
                'yorum': durum.yorum if durum.yorum else ''
            })
        
        # AI prompt'ta gösterilecek liste
        detay_liste_str = ', '.join([f"{ezber['sira']}. {ezber['ad']} ({ezber['durum']})" for ezber in elifba_detay_listesi])
        self.stdout.write(f"DETAYLI ELİF BA EZBERLERİ LİSTESİ:")
        self.stdout.write(detay_liste_str)
        
        self.stdout.write(f"\nÖğrenci detay URL: /admin-paneli/ogrenci/detay/{ogrenci.id}/")
        
        # Ogrenci_detay view'ındaki aynı sorguyu simüle edelim
        self.stdout.write(f"\n=== VIEW'DAKİ HESAPLAMALARI SİMÜLE EDİYORUZ ===")
        
        # Prefetch kullanarak veriyi çek (view'da olduğu gibi)
        from django.db.models import Prefetch
        ogrenci_with_prefetch = Ogrenci.objects.prefetch_related(
            Prefetch('elifbaezberdurumu_set', queryset=ElifBaEzberDurumu.objects.select_related('ezber'))
        ).get(id=ogrenci.id)
        
        elifba_durumlari_prefetch = ogrenci_with_prefetch.elifbaezberdurumu_set.all()
        
        # Aggregate işlemi
        from django.db.models import Count, Q
        elifba_durumlari_istatistik = elifba_durumlari_prefetch.aggregate(
            tamamlanan=Count('id', filter=Q(durum='TAMAMLANDI')),
            devam_eden=Count('id', filter=Q(durum='DEVAM')),
            baslamayan=Count('id', filter=Q(durum='BASLAMADI'))
        )
        
        self.stdout.write(f"View'daki aggregate sonucu: {elifba_durumlari_istatistik}")
        
        # Final değerler
        tamamlanan_elifba = elifba_durumlari_istatistik['tamamlanan'] or 0
        devam_eden_elifba = elifba_durumlari_istatistik['devam_eden'] or 0
        baslamayan_elifba = elifba_durumlari_istatistik['baslamayan'] or 0
        
        self.stdout.write(f"Template'e gönderilecek değerler:")
        self.stdout.write(f"  tamamlanan_elifba: {tamamlanan_elifba}")
        self.stdout.write(f"  devam_eden_elifba: {devam_eden_elifba}")
        self.stdout.write(f"  baslamayan_elifba: {baslamayan_elifba}")
        
        self.stdout.write(self.style.SUCCESS('Elif Ba detay analizi tamamlandı!'))