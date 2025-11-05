from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import uuid

# Create your models here.

class SiteContent(models.Model):
    slug = models.SlugField(unique=True)  # örn: 'hakkimda', 'anasayfa-alt-metin'
    baslik = models.CharField(max_length=200, blank=True)
    icerik = models.TextField(blank=True)
    guncellenme_tarihi = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug
    
class category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'

class yazi(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    imageUrl = models.ImageField(upload_to='uploads', blank=True, null=True)
    date = models.DateField(default=timezone.now)  # Varsayılan olarak bugünün tarihi
    isActive = models.BooleanField(default=True)
    slug = models.SlugField(default="", null=False,unique=True,db_index=True)
    tarih = models.DateTimeField(auto_now_add=True)  # Otomatik oluşturulma tarihi
    category = models.ForeignKey(category,default=1, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        # Slug oluştur - Arapça/Türkçe karakterler için UUID ekle
        base_slug = slugify(self.title)
        
        # Eğer slug boşsa (Arapça vb.) veya çok kısaysa, UUID ekle
        if not base_slug or len(base_slug) < 3:
            base_slug = str(uuid.uuid4())[:8]
        
        # Slug benzersiz mi kontrol et
        if not self.pk:  # Yeni kayıt
            original_slug = base_slug
            counter = 1
            while yazi.objects.filter(slug=base_slug).exists():
                base_slug = f"{original_slug}-{counter}"
                counter += 1
        
        self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} {self.date}'
