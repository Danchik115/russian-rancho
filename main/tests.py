import json
from datetime import date
from io import StringIO
from unittest.mock import MagicMock, patch
from urllib import error as url_error

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from main.models import BirthdaySubscriber
from main.telegram_utils import send_telegram_message


class MainPagesTests(TestCase):
    def test_all_public_pages_return_200(self):
        urls = [
            reverse("main:home"),
            reverse("main:about"),
            reverse("main:families"),
            reverse("main:kids"),
            reverse("main:couples"),
            reverse("main:groups"),
            reverse("main:events"),
            reverse("main:prices"),
            reverse("main:gallery"),
            reverse("main:nedvizhimost"),
            reverse("main:domik_u_lesa"),
            reverse("main:domik_u_pruda"),
            reverse("main:teplaya_besedka_1"),
            reverse("main:teplaya_besedka_2"),
            reverse("main:letnyaya_besedka"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_home_contains_auth_and_trust_blocks(self):
        response = self.client.get(reverse("main:home"))
        self.assertContains(response, "Личный профиль гостя")
        self.assertContains(response, "Нам доверяют отдых и важные события")
        self.assertContains(response, "О нас пишут и нас рекомендуют")


class TelegramApiTests(TestCase):
    def test_telegram_api_rejects_get(self):
        response = self.client.get(reverse("main:telegram_api"))
        self.assertEqual(response.status_code, 405)

    @patch("main.views.send_telegram_message", return_value=(True, ""))
    def test_telegram_api_success(self, send_mock):
        payload = {
            "name": "Иван",
            "phone": "+79990000000",
            "interest": "family",
            "date": "2026-03-20",
            "people": "4",
            "comment": "Тест",
        }
        response = self.client.post(
            reverse("main:telegram_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        send_mock.assert_called_once()
        sent_message = send_mock.call_args.args[0]
        self.assertIn("Новая заявка с сайта Русское Ранчо", sent_message)
        self.assertIn("Иван", sent_message)
        self.assertIn("+79990000000", sent_message)

    def test_telegram_api_invalid_json(self):
        response = self.client.post(
            reverse("main:telegram_api"),
            data="{bad_json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch("main.views.send_telegram_message", return_value=(False, "boom"))
    def test_telegram_api_telegram_error(self, _send_mock):
        response = self.client.post(
            reverse("main:telegram_api"),
            data=json.dumps({"name": "Иван"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["error"], "Failed to send to Telegram")


class BirthdaySubscribeApiTests(TestCase):
    def test_birthday_subscribe_rejects_get(self):
        response = self.client.get(reverse("main:birthday_subscribe_api"))
        self.assertEqual(response.status_code, 405)

    def test_birthday_subscribe_creates_record(self):
        payload = {
            "first_name": "Иван",
            "last_name": "Петров",
            "phone": "+79990000000",
            "birth_date": "2000-05-12",
        }
        response = self.client.post(
            reverse("main:birthday_subscribe_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["created"])
        self.assertEqual(BirthdaySubscriber.objects.count(), 1)
        subscriber = BirthdaySubscriber.objects.get(phone="+79990000000")
        self.assertEqual(subscriber.first_name, "Иван")
        self.assertEqual(subscriber.last_name, "Петров")

    def test_birthday_subscribe_updates_existing_by_phone(self):
        BirthdaySubscriber.objects.create(
            first_name="Старое",
            last_name="Имя",
            phone="+79990000000",
            birth_date=date(1995, 1, 1),
        )
        payload = {
            "first_name": "Новое",
            "last_name": "Имя",
            "phone": "+79990000000",
            "birth_date": "1996-02-02",
        }
        response = self.client.post(
            reverse("main:birthday_subscribe_api"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        self.assertFalse(data["created"])
        self.assertEqual(BirthdaySubscriber.objects.count(), 1)
        subscriber = BirthdaySubscriber.objects.get(phone="+79990000000")
        self.assertEqual(subscriber.first_name, "Новое")
        self.assertEqual(subscriber.birth_date, date(1996, 2, 2))

    def test_birthday_subscribe_validation_errors(self):
        response = self.client.post(
            reverse("main:birthday_subscribe_api"),
            data=json.dumps({"first_name": "Иван"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "All fields are required")

        response = self.client.post(
            reverse("main:birthday_subscribe_api"),
            data=json.dumps(
                {
                    "first_name": "Иван",
                    "last_name": "Петров",
                    "phone": "+79990000000",
                    "birth_date": "12-05-2000",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Birth date must be YYYY-MM-DD")

    def test_birthday_subscribe_invalid_json(self):
        response = self.client.post(
            reverse("main:birthday_subscribe_api"),
            data="{bad_json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON body")


class TelegramUtilsTests(TestCase):
    @patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "123", "TELEGRAM_API_BASE": "https://api.telegram.org"},
        clear=False,
    )
    @patch("main.telegram_utils.request.urlopen")
    def test_send_telegram_message_success(self, urlopen_mock):
        response = MagicMock()
        response.read.return_value = b'{"ok": true}'
        urlopen_mock.return_value.__enter__.return_value = response

        ok, details = send_telegram_message("hello")

        self.assertTrue(ok)
        self.assertEqual(details, "")
        urlopen_mock.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    def test_send_telegram_message_missing_env(self):
        ok, details = send_telegram_message("hello")
        self.assertFalse(ok)
        self.assertIn("not configured", details)

    @patch.dict(
        "os.environ",
        {"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_CHAT_ID": "123"},
        clear=False,
    )
    @patch("main.telegram_utils.request.urlopen", side_effect=url_error.URLError("network down"))
    def test_send_telegram_message_url_error(self, _urlopen_mock):
        ok, details = send_telegram_message("hello")
        self.assertFalse(ok)
        self.assertIn("network down", details)


class SendBirthdayNotificationsCommandTests(TestCase):
    def setUp(self):
        self.today = date(2026, 3, 10)
        BirthdaySubscriber.objects.create(
            first_name="Иван",
            last_name="Петров",
            phone="+79990000001",
            birth_date=date(2000, 3, 13),
        )
        BirthdaySubscriber.objects.create(
            first_name="Мария",
            last_name="Сидорова",
            phone="+79990000002",
            birth_date=date(2001, 3, 13),
            last_birthday_notified_on=self.today,
        )

    @patch("main.management.commands.send_birthday_notifications.timezone.localdate")
    @patch("main.management.commands.send_birthday_notifications.send_telegram_message")
    def test_command_sends_only_not_notified_today(self, send_mock, localdate_mock):
        localdate_mock.return_value = self.today
        send_mock.return_value = (True, "")
        stdout = StringIO()

        call_command("send_birthday_notifications", stdout=stdout)

        send_mock.assert_called_once()
        msg = send_mock.call_args.args[0]
        self.assertIn("Иван Петров", msg)
        self.assertNotIn("Мария Сидорова", msg)

        ivan = BirthdaySubscriber.objects.get(phone="+79990000001")
        maria = BirthdaySubscriber.objects.get(phone="+79990000002")
        self.assertEqual(ivan.last_birthday_notified_on, self.today)
        self.assertEqual(maria.last_birthday_notified_on, self.today)

    @patch("main.management.commands.send_birthday_notifications.timezone.localdate")
    @patch("main.management.commands.send_birthday_notifications.send_telegram_message")
    def test_command_force_includes_already_notified(self, send_mock, localdate_mock):
        localdate_mock.return_value = self.today
        send_mock.return_value = (True, "")

        call_command("send_birthday_notifications", "--force")

        msg = send_mock.call_args.args[0]
        self.assertIn("Иван Петров", msg)
        self.assertIn("Мария Сидорова", msg)

    @patch("main.management.commands.send_birthday_notifications.timezone.localdate")
    @patch("main.management.commands.send_birthday_notifications.send_telegram_message")
    def test_command_dry_run_does_not_send(self, send_mock, localdate_mock):
        localdate_mock.return_value = self.today
        stdout = StringIO()

        call_command("send_birthday_notifications", "--dry-run", stdout=stdout)

        send_mock.assert_not_called()
        output = stdout.getvalue()
        self.assertIn("DRY RUN", output)

    @patch("main.management.commands.send_birthday_notifications.timezone.localdate")
    @patch("main.management.commands.send_birthday_notifications.send_telegram_message")
    def test_command_days_ahead_zero(self, send_mock, localdate_mock):
        localdate_mock.return_value = self.today
        send_mock.return_value = (True, "")
        BirthdaySubscriber.objects.create(
            first_name="Сегодня",
            last_name="Именинник",
            phone="+79990000003",
            birth_date=date(1990, 3, 10),
        )

        call_command("send_birthday_notifications", "--days-ahead", "0")

        msg = send_mock.call_args.args[0]
        self.assertIn("Сегодня Именинник", msg)

    @patch("main.management.commands.send_birthday_notifications.timezone.localdate")
    @patch("main.management.commands.send_birthday_notifications.send_telegram_message")
    def test_command_no_birthdays(self, send_mock, localdate_mock):
        localdate_mock.return_value = date(2026, 3, 1)
        stdout = StringIO()

        call_command("send_birthday_notifications", stdout=stdout)

        send_mock.assert_not_called()
        self.assertIn("No birthdays to notify", stdout.getvalue())

    @patch("main.management.commands.send_birthday_notifications.timezone.localdate")
    @patch("main.management.commands.send_birthday_notifications.send_telegram_message")
    def test_command_telegram_failure_raises(self, send_mock, localdate_mock):
        localdate_mock.return_value = self.today
        send_mock.return_value = (False, "tg down")

        with self.assertRaises(CommandError):
            call_command("send_birthday_notifications")

    def test_command_negative_days_ahead_raises(self):
        with self.assertRaises(CommandError):
            call_command("send_birthday_notifications", "--days-ahead", "-1")


class CabinetFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username="+79991112233",
            password=self.password,
            first_name="Анна",
            last_name="Иванова",
        )
        self.subscriber = BirthdaySubscriber.objects.create(
            user=self.user,
            first_name="Анна",
            last_name="Иванова",
            phone="+79991112233",
            birth_date=date(1999, 8, 20),
        )

    def test_cabinet_login_page_available(self):
        response = self.client.get(reverse("main:cabinet_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Войти в кабинет")

    def test_cabinet_requires_login(self):
        response = self.client.get(reverse("main:cabinet"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("main:cabinet_login"), response["Location"])

    def test_cabinet_login_success_and_access(self):
        response = self.client.post(
            reverse("main:cabinet_login"),
            data={"phone": self.subscriber.phone, "password": self.password},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ваш личный кабинет")
        self.assertContains(response, "Анна")
        self.assertContains(response, self.subscriber.phone)

    def test_cabinet_login_invalid_credentials(self):
        response = self.client.post(
            reverse("main:cabinet_login"),
            data={"phone": self.subscriber.phone, "password": "badpass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный номер телефона или пароль")

    def test_cabinet_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("main:cabinet_register"),
            data={
                "first_name": "Иван",
                "last_name": "Петров",
                "phone": "+79990000077",
                "birth_date": "2001-01-01",
                "password": "Secret123!",
                "password_confirm": "Secret123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ваш личный кабинет")
        self.assertTrue(BirthdaySubscriber.objects.filter(phone="+79990000077").exists())

    def test_cabinet_register_links_existing_profile(self):
        BirthdaySubscriber.objects.create(
            first_name="Мария",
            last_name="Соколова",
            phone="+79990000088",
            birth_date=date(2002, 2, 2),
        )
        response = self.client.post(
            reverse("main:cabinet_register"),
            data={
                "first_name": "Мария",
                "last_name": "Соколова",
                "phone": "+79990000088",
                "birth_date": "2002-02-02",
                "password": "Secret123!",
                "password_confirm": "Secret123!",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        linked = BirthdaySubscriber.objects.get(phone="+79990000088")
        self.assertIsNotNone(linked.user)

    @patch("main.views.send_telegram_message", return_value=(True, ""))
    def test_cabinet_submit_prefilled_request_success(self, send_mock):
        self.client.post(
            reverse("main:cabinet_login"),
            data={"phone": self.subscriber.phone, "password": self.password},
        )
        response = self.client.post(
            reverse("main:cabinet"),
            data={"interest": "family", "date": "2026-03-21", "people": "3", "comment": "Тест"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Заявка отправлена")
        send_mock.assert_called_once()
        message = send_mock.call_args.args[0]
        self.assertIn("Заявка из личного кабинета", message)
        self.assertIn("Анна Иванова", message)
        self.assertIn(self.subscriber.phone, message)

    @patch("main.views.send_telegram_message", return_value=(False, "network"))
    def test_cabinet_submit_request_error(self, _send_mock):
        self.client.post(
            reverse("main:cabinet_login"),
            data={"phone": self.subscriber.phone, "password": self.password},
        )
        response = self.client.post(
            reverse("main:cabinet"),
            data={"interest": "family"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Не удалось отправить заявку")
