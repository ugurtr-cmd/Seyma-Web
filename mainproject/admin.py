from django.contrib import admin
from .models import (
    Ogrenci, EzberSuresi, EzberKaydi, Ders, DersNotu, SinavSonucu,
    ElifBaEzberi, ElifBaEzberDurumu, Alinti
)

@admin.register(Ogrenci)
class OgrenciAdmin(admin.ModelAdmin):
    list_display = ['ad_soyad', 'seviye', 'kayit_tarihi', 'tamamlanan_ezber_sayisi', 'tamamlanan_elifba_sayisi']
    list_filter = ['seviye', 'kayit_tarihi']
    search_fields = ['ad_soyad']
    date_hierarchy = 'kayit_tarihi'

@admin.register(ElifBaEzberi)
class ElifBaEzberiAdmin(admin.ModelAdmin):
    list_display = ['sira', 'ad', 'tahmini_sure']
    list_editable = ['ad', 'tahmini_sure']
    ordering = ['sira']

@admin.register(ElifBaEzberDurumu)
class ElifBaEzberDurumuAdmin(admin.ModelAdmin):
    list_display = ['ogrenci', 'ezber', 'durum', 'baslama_tarihi', 'bitis_tarihi']
    list_filter = ['durum', 'ezber']
    search_fields = ['ogrenci__ad_soyad', 'ezber__ad']
    date_hierarchy = 'baslama_tarihi'

@admin.register(EzberSuresi)
class EzberSuresiAdmin(admin.ModelAdmin):
    list_display = ['sira', 'ad', 'tahmini_sure']
    list_editable = ['ad', 'tahmini_sure']
    ordering = ['sira']

@admin.register(EzberKaydi)
class EzberKaydiAdmin(admin.ModelAdmin):
    list_display = ['ogrenci', 'sure', 'durum', 'ilerleme', 'baslama_tarihi', 'bitis_tarihi']
    list_filter = ['durum', 'sure']
    search_fields = ['ogrenci__ad_soyad', 'sure__ad']

@admin.register(Ders)
class DersAdmin(admin.ModelAdmin):
    list_display = ['ad', 'tur']
    list_filter = ['tur']

@admin.register(DersNotu)
class DersNotuAdmin(admin.ModelAdmin):
    list_display = ['ogrenci', 'ders', 'not_degeri', 'tarih']
    list_filter = ['ders', 'tarih']
    search_fields = ['ogrenci__ad_soyad']

@admin.register(SinavSonucu)
class SinavSonucuAdmin(admin.ModelAdmin):
    list_display = ['ogrenci', 'ders', 'sinav_tipi', 'puan', 'tarih']
    list_filter = ['sinav_tipi', 'ders', 'tarih']
    search_fields = ['ogrenci__ad_soyad']

@admin.register(Alinti)
class AlintiAdmin(admin.ModelAdmin):
    list_display = ['quote_text', 'author', 'category', 'isActive', 'created_at']
    list_filter = ['isActive', 'category', 'created_at']
    search_fields = ['quote_text', 'author']
    list_editable = ['isActive']