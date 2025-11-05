"""
Akıllı Bildirimler için View fonksiyonları
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import AkilliBildirim


@login_required
@require_POST
def bildirim_okundu(request, bildirim_id):
    """Bildirimi okundu olarak işaretle"""
    try:
        bildirim = get_object_or_404(AkilliBildirim, id=bildirim_id)
        bildirim.okundu_olarak_isaretle()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def yeni_gunluk_bildirim(request):
    """Yeni günlük motivasyon bildirim oluştur"""
    try:
        from . import gemini_service
        bildirim = gemini_service.gunluk_motivasyon_olustur()
        return JsonResponse({
            'success': True,
            'baslik': bildirim.baslik,
            'mesaj': bildirim.mesaj
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
