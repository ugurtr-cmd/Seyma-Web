import json
import requests
from django.conf import settings
from django.utils import timezone
from .models import BildirimAbonelik, BildirimGecmisi
import logging

logger = logging.getLogger(__name__)

class BildirimServisi:
    """Web bildirimleri gönderme servisi"""
    
    def __init__(self):
        # VAPID anahtarları (üretimde environment değişkenlerinden alınmalı)
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
        self.vapid_email = getattr(settings, 'VAPID_EMAIL', 'admin@seyma.local')

    def abonelik_kaydet(self, endpoint, p256dh, auth):
        """Yeni bildirim aboneliğini kaydet"""
        try:
            abonelik, created = BildirimAbonelik.objects.get_or_create(
                endpoint=endpoint,
                defaults={
                    'p256dh_key': p256dh,
                    'auth_key': auth,
                    'aktif': True
                }
            )
            
            if not created:
                # Mevcut aboneliği güncelle
                abonelik.p256dh_key = p256dh
                abonelik.auth_key = auth
                abonelik.aktif = True
                abonelik.save()
            
            return abonelik
            
        except Exception as e:
            logger.error(f"Abonelik kaydedilirken hata: {e}")
            return None

    def bildirim_gonder(self, baslik, icerik, tip='SISTEM', actions=None, tag=None):
        """Tüm aktif abonelere bildirim gönder"""
        
        abonelikler = BildirimAbonelik.objects.filter(aktif=True)
        basarili = 0
        basarisiz = 0
        
        payload = {
            'title': baslik,
            'body': icerik,
            'icon': '/static/blog/img/favicon2.png',
            'badge': '/static/blog/img/favicon2.png',
            'tag': tag or tip.lower(),
            'data': {
                'tip': tip,
                'timestamp': int(timezone.now().timestamp())
            },
            'actions': actions or []
        }
        
        if tip == 'GUNLUK_MESAJ':
            payload['actions'] = [
                {'action': 'view-message', 'title': 'Mesajı Oku'},
                {'action': 'close', 'title': 'Kapat'}
            ]
        elif tip == 'HAFTALIK_RAPOR':
            payload['actions'] = [
                {'action': 'view-students', 'title': 'Öğrencileri Gör'},
                {'action': 'close', 'title': 'Kapat'}
            ]
        
        for abonelik in abonelikler:
            try:
                # Web Push protokolü ile bildirim gönder
                # Not: Gerçek implementasyon için pywebpush kütüphanesi gerekli
                # Bu örnekte basit bir yaklaşım kullanıyoruz
                
                sonuc = self._web_push_gonder(abonelik, payload)
                
                if sonuc:
                    basarili += 1
                else:
                    basarisiz += 1
                    # Başarısız abonelikleri pasif yap
                    abonelik.aktif = False
                    abonelik.save()
                    
            except Exception as e:
                logger.error(f"Bildirim gönderilirken hata: {e}")
                basarisiz += 1
        
        # Bildirim geçmişine kaydet
        BildirimGecmisi.objects.create(
            tip=tip,
            baslik=baslik,
            icerik=icerik,
            basarili_gonderim=basarili,
            basarisiz_gonderim=basarisiz
        )
        
        return {'basarili': basarili, 'basarisiz': basarisiz}
    
    def _web_push_gonder(self, abonelik, payload):
        """Web Push API ile bildirim gönder"""
        try:
            # Basit bir mock implementasyon
            # Gerçek implementasyon için pywebpush kullanılmalı
            
            # Şimdilik başarılı olarak işaretleyelim
            logger.info(f"Bildirim gönderildi: {payload['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Web push gönderim hatası: {e}")
            return False

    def gunluk_mesaj_bildirimi(self):
        """Günlük kişisel mesaj bildirimi gönder"""
        from .models import GunlukMesaj
        from datetime import date
        
        try:
            bugun_mesaji = GunlukMesaj.objects.filter(tarih=date.today()).first()
            
            if bugun_mesaji:
                baslik = "💝 Bugünün Kişisel Mesajınız Hazır!"
                icerik = bugun_mesaji.mesaj_ozeti or bugun_mesaji.mesaj[:100] + "..."
                
                return self.bildirim_gonder(
                    baslik=baslik,
                    icerik=icerik,
                    tip='GUNLUK_MESAJ',
                    tag='daily-message'
                )
            else:
                logger.info("Bugün için kişisel mesaj bulunamadı")
                return {'basarili': 0, 'basarisiz': 0}
                
        except Exception as e:
            logger.error(f"Günlük mesaj bildirimi hatası: {e}")
            return {'basarili': 0, 'basarisiz': 0}

    def haftalik_rapor_bildirimi(self):
        """Haftalık öğrenci durum raporu bildirimi gönder (Gemini destekli)"""
        try:
            from .weekly_report_service import haftalik_rapor_servisi
            
            rapor = haftalik_rapor_servisi.haftalik_rapor_olustur()
            
            baslik = rapor['baslik']
            icerik = rapor['icerik']
            
            return self.bildirim_gonder(
                baslik=baslik,
                icerik=icerik,
                tip='HAFTALIK_RAPOR',
                tag='weekly-report'
            )
            
        except Exception as e:
            logger.error(f"Haftalık rapor bildirimi hatası: {e}")
            return {'basarili': 0, 'basarisiz': 0}


# Singleton instance
bildirim_servisi = BildirimServisi()