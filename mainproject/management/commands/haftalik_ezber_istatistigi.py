"""
Haftalık ezber istatistiği bildirimi oluşturan management command
Kullanım: python manage.py haftalik_ezber_istatistigi
"""
from django.core.management.base import BaseCommand
from mainproject import gemini_service


class Command(BaseCommand):
    help = 'Haftalık ezber istatistiği bildirimi oluşturur'

    def handle(self, *args, **options):
        self.stdout.write('Haftalık ezber istatistiği oluşturuluyor...')
        
        try:
            bildirim = gemini_service.haftalik_ezber_istatistigi()
            self.stdout.write(self.style.SUCCESS(f'✅ İstatistik oluşturuldu: {bildirim.baslik}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Hata: {e}'))
