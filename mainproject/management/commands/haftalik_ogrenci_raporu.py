"""
Haftalık öğrenci raporu oluşturan management command
Kullanım: python manage.py haftalik_ogrenci_raporu
"""
from django.core.management.base import BaseCommand
from mainproject import gemini_service


class Command(BaseCommand):
    help = 'Haftalık öğrenci performans raporu oluşturur'

    def handle(self, *args, **options):
        self.stdout.write('Haftalık öğrenci raporu oluşturuluyor...')
        
        try:
            bildirim = gemini_service.haftalik_ogrenci_raporu()
            if bildirim:
                self.stdout.write(self.style.SUCCESS(f'✅ Rapor oluşturuldu: {bildirim.baslik}'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Öğrenci verisi bulunamadı'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Hata: {e}'))
