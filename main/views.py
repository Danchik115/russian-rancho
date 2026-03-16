import json
import os
from urllib import error, request

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView


class PageView(TemplateView):
    """Рендер страницы с общим шаблоном и активным пунктом меню."""
    active_nav = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_nav'] = self.active_nav
        return context


def home(request):
    return render(request, 'main/index.html', {'active_nav': None})


def about_page(request):
    return render(request, 'main/about.html', {'active_nav': 'about'})


def families_page(request):
    return render(request, 'main/families.html', {'active_nav': 'families'})


def kids_page(request):
    return render(request, 'main/kids.html', {'active_nav': 'kids'})


def couples_page(request):
    return render(request, 'main/couples.html', {'active_nav': 'couples'})


def groups_page(request):
    return render(request, 'main/groups.html', {'active_nav': 'groups'})


def events_page(request):
    return render(request, 'main/events.html', {'active_nav': 'events'})


def prices_page(request):
    return render(request, 'main/prices.html', {'active_nav': 'prices'})


def gallery_page(request):
    return render(request, 'main/gallery.html', {'active_nav': None})


def nedvizhimost_page(request):
    return render(request, 'main/nedvizhimost.html', {'active_nav': 'nedvizhimost'})


INTEREST_LABELS = {
    "family": "Семейные программы",
    "kids": "Форматы для детей",
    "couples": "Свидания и пикники",
    "groups": "Групповые выезды",
    "events": "Мероприятия и афиша",
    "nedvizhimost": "Тепло и уют для вас (домики, беседки)",
    "certificate": "Подарочный сертификат",
    "prices": "Цены и условия",
    "other": "Другое",
}


def _build_message(body):
    name = body.get("name", "")
    phone = body.get("phone", "")
    interest = body.get("interest", "")
    date = body.get("date", "")
    people = body.get("people", "")
    comment = body.get("comment", "")
    interest_label = INTEREST_LABELS.get(interest, interest) if interest else ""

    lines = [
        "🟢 Новая заявка с сайта Русское Ранчо",
        "",
        f"👤 Имя: {name or '—'}",
        f"📞 Телефон: {phone or '—'}",
    ]
    if interest_label:
        lines.append(f"🎯 Интересует: {interest_label}")
    if date:
        lines.append(f"📅 Дата: {date}")
    if people:
        lines.append(f"👥 Количество человек: {people}")
    if comment:
        lines.append(f"💬 Комментарий: {comment}")
    return "\n".join(lines)


@csrf_exempt
@require_POST
def telegram_api(request_obj):
    try:
        body = json.loads(request_obj.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        return JsonResponse({"error": "Server not configured for Telegram"}, status=500)

    message = _build_message(body)
    api_base = os.getenv("TELEGRAM_API_BASE", "https://api.telegram.org").rstrip("/")

    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")

    tg_req = request.Request(
        f"{api_base}/bot{bot_token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(tg_req, timeout=15) as tg_res:
            tg_data = json.loads(tg_res.read().decode("utf-8") or "{}")
    except error.URLError as exc:
        reason = str(getattr(exc, "reason", exc))
        return JsonResponse({"error": "Failed to send to Telegram", "details": reason}, status=500)

    if not tg_data.get("ok"):
        description = ""
        if isinstance(tg_data.get("description"), str):
            description = tg_data["description"]
        return JsonResponse({"error": "Failed to send to Telegram", "details": description}, status=500)

    return JsonResponse({"ok": True})
