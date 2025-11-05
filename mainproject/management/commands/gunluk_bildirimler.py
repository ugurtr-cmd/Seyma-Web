"""
Günlük bildirimler oluşturan management command
Kullanım: python manage.py gunluk_bildirimler
"""
from django.core.management.base import BaseCommand
from mainproject import gemini_service


class Command(BaseCommand):
    help = 'Günlük motivasyon bildirimi oluşturur'

    def handle(self, *args, **options):
        self.stdout.write('Günlük motivasyon bildirimi oluşturuluyor...')
        
        try:
            bildirim = gemini_service.gunluk_motivasyon_olustur()
            self.stdout.write(self.style.SUCCESS(f'✅ Bildirim oluşturuldu: {bildirim.baslik}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Hata: {e}'))
