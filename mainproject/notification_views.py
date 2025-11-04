from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
from .notification_service import bildirim_servisi

@csrf_exempt
@require_http_methods(["POST"])
def bildirim_abonelik_kaydet(request):
    """Bildirim aboneliği kaydet"""
    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        p256dh = data.get('keys', {}).get('p256dh')
        auth = data.get('keys', {}).get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return JsonResponse({
                'success': False,
                'error': 'Eksik abonelik bilgileri'
            }, status=400)
        
        abonelik = bildirim_servisi.abonelik_kaydet(endpoint, p256dh, auth)
        
        if abonelik:
            return JsonResponse({
                'success': True,
                'message': 'Abonelik başarıyla kaydedildi'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Abonelik kaydedilemedi'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def test_bildirim_gonder(request):
    """Test bildirimi gönder"""
    try:
        sonuc = bildirim_servisi.bildirim_gonder(
            baslik="🧪 Test Bildirimi",
            icerik="Bu bir test bildirimidir. Bildirimler doğru çalışıyor!",
            tip='SISTEM'
        )
        
        return JsonResponse({
            'success': True,
            'sonuc': sonuc
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def gunluk_mesaj_bildirimi_api(request):
    """Günlük mesaj bildirimi gönder"""
    try:
        sonuc = bildirim_servisi.gunluk_mesaj_bildirimi()
        
        return JsonResponse({
            'success': True,
            'sonuc': sonuc
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt  
@require_http_methods(["POST"])
def haftalik_rapor_bildirimi_api(request):
    """Haftalık rapor bildirimi gönder"""
    try:
        sonuc = bildirim_servisi.haftalik_rapor_bildirimi()
        
        return JsonResponse({
            'success': True,
            'sonuc': sonuc
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)