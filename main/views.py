import json
from datetime import date

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from .models import BirthdaySubscriber
from .telegram_utils import send_telegram_message


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


def domik_u_lesa_page(request):
    return render(request, "main/properties/domik_u_lesa.html", {"active_nav": None})


def domik_u_pruda_page(request):
    return render(request, "main/properties/domik_u_pruda.html", {"active_nav": None})


def teplaya_besedka_1_page(request):
    return render(request, "main/properties/teplaya_besedka_1.html", {"active_nav": None})


def teplaya_besedka_2_page(request):
    return render(request, "main/properties/teplaya_besedka_2.html", {"active_nav": None})


def letnyaya_besedka_page(request):
    return render(request, "main/properties/letnyaya_besedka.html", {"active_nav": None})


def _get_logged_subscriber(request):
    if not request.user.is_authenticated:
        return None
    try:
        return BirthdaySubscriber.objects.get(user=request.user)
    except BirthdaySubscriber.DoesNotExist:
        return None


def cabinet_register_page(request):
    if request.user.is_authenticated and _get_logged_subscriber(request):
        return redirect("main:cabinet")

    if request.method == "POST":
        first_name = str(request.POST.get("first_name", "")).strip()
        last_name = str(request.POST.get("last_name", "")).strip()
        phone = str(request.POST.get("phone", "")).strip()
        birth_date_raw = str(request.POST.get("birth_date", "")).strip()
        password = str(request.POST.get("password", ""))
        password_confirm = str(request.POST.get("password_confirm", ""))

        if not first_name or not last_name or not phone or not birth_date_raw or not password:
            messages.error(request, "Заполните все поля.")
            return render(request, "main/cabinet_register.html", {"active_nav": None})

        if password != password_confirm:
            messages.error(request, "Пароли не совпадают.")
            return render(request, "main/cabinet_register.html", {"active_nav": None})

        try:
            birth_date = date.fromisoformat(birth_date_raw)
        except ValueError:
            messages.error(request, "Неверный формат даты рождения.")
            return render(request, "main/cabinet_register.html", {"active_nav": None})

        if User.objects.filter(username=phone).exists():
            messages.error(request, "Пользователь с таким номером уже существует. Войдите в кабинет.")
            return redirect("main:cabinet_login")

        subscriber = BirthdaySubscriber.objects.filter(phone=phone).first()
        if subscriber and subscriber.birth_date != birth_date:
            messages.error(request, "Профиль с таким телефоном уже есть, но дата рождения не совпадает.")
            return render(request, "main/cabinet_register.html", {"active_nav": None})

        user = User.objects.create_user(
            username=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        if subscriber:
            subscriber.first_name = first_name
            subscriber.last_name = last_name
            subscriber.birth_date = birth_date
            subscriber.user = user
            subscriber.save()
        else:
            subscriber = BirthdaySubscriber.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                birth_date=birth_date,
            )

        registration_message = "\n".join(
            [
                "🆕 Новая регистрация в личном кабинете",
                "",
                f"👤 Имя: {subscriber.first_name} {subscriber.last_name}",
                f"📞 Телефон: {subscriber.phone}",
                f"🎂 Дата рождения: {subscriber.birth_date.isoformat()}",
            ]
        )
        # Нотификация не должна блокировать регистрацию, если Telegram временно недоступен.
        send_telegram_message(registration_message)

        login(request, user)
        messages.success(request, "Регистрация выполнена. Добро пожаловать в личный кабинет.")
        return redirect("main:cabinet")

    return render(request, "main/cabinet_register.html", {"active_nav": None})


def cabinet_login_page(request):
    if request.user.is_authenticated and _get_logged_subscriber(request):
        return redirect("main:cabinet")

    next_url = request.GET.get("next", "")

    if request.method == "POST":
        phone = str(request.POST.get("phone", "")).strip()
        password = str(request.POST.get("password", ""))
        if not phone or not password:
            messages.error(request, "Введите номер телефона и пароль.")
            return render(request, "main/cabinet_login.html", {"active_nav": None})

        user = authenticate(request, username=phone, password=password)
        if not user:
            messages.error(request, "Неверный номер телефона или пароль.")
            return render(request, "main/cabinet_login.html", {"active_nav": None})

        if not BirthdaySubscriber.objects.filter(user=user).exists():
            messages.error(request, "Для этого пользователя не найден профиль. Пройдите регистрацию.")
            return render(request, "main/cabinet_login.html", {"active_nav": None})

        login(request, user)
        messages.success(request, "Вы успешно вошли в личный кабинет.")
        if next_url.startswith("/"):
            return redirect(next_url)
        return redirect("main:cabinet")

    return render(request, "main/cabinet_login.html", {"active_nav": None})


def cabinet_logout(request):
    logout(request)
    messages.success(request, "Вы вышли из личного кабинета.")
    return redirect("main:home")


def cabinet_page(request):
    subscriber = _get_logged_subscriber(request)
    if not subscriber:
        return redirect(f"{reverse('main:cabinet_login')}?next={reverse('main:cabinet')}")

    if request.method == "POST":
        interest = str(request.POST.get("interest", "")).strip()
        visit_date = str(request.POST.get("date", "")).strip()
        people = str(request.POST.get("people", "")).strip()
        comment = str(request.POST.get("comment", "")).strip()

        if not interest:
            messages.error(request, "Выберите, что вас интересует.")
            return render(request, "main/cabinet.html", {"active_nav": None, "subscriber": subscriber})

        interest_label = INTEREST_LABELS.get(interest, interest)
        lines = [
            "🟣 Заявка из личного кабинета Русского Ранчо",
            "",
            f"👤 Имя: {subscriber.first_name} {subscriber.last_name}",
            f"📞 Телефон: {subscriber.phone}",
            f"🎂 Дата рождения: {subscriber.birth_date.isoformat()}",
            f"🎯 Интересует: {interest_label}",
        ]
        if visit_date:
            lines.append(f"📅 Дата визита: {visit_date}")
        if people:
            lines.append(f"👥 Количество человек: {people}")
        if comment:
            lines.append(f"💬 Комментарий: {comment}")

        ok, details = send_telegram_message("\n".join(lines))
        if ok:
            messages.success(request, "Заявка отправлена. Мы скоро свяжемся с вами.")
            return redirect("main:cabinet")
        messages.error(request, f"Не удалось отправить заявку: {details}")

    return render(request, "main/cabinet.html", {"active_nav": None, "subscriber": subscriber})


INTEREST_LABELS = {
    "family": "Семейные программы",
    "kids": "Форматы для детей",
    "couples": "Свидания и пикники",
    "groups": "Групповые выезды",
    "events": "Мероприятия и афиша",
    "nedvizhimost": "Теплые и уютные места для вас (домики, беседки)",
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

    message = _build_message(body)
    ok, details = send_telegram_message(message)
    if not ok:
        description = details if isinstance(details, str) else ""
        return JsonResponse({"error": "Failed to send to Telegram", "details": description}, status=500)

    return JsonResponse({"ok": True})
