import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sseyma.settings')
django.setup()

from blog.models import yazi
import uuid

# Boş slug'ları bul
bos_sluglar = yazi.objects.filter(slug='')
print(f'Boş slug sayısı: {bos_sluglar.count()}')

# Her birini düzelt
for y in bos_sluglar:
    y.slug = str(uuid.uuid4())[:8]
    y.save()
    print(f'Düzeltildi: {y.title} -> {y.slug}')

print('Tüm boş slug\'lar düzeltildi!')
