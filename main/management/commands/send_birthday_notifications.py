from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from main.models import BirthdaySubscriber
from main.telegram_utils import send_telegram_message


class Command(BaseCommand):
    help = "Send Telegram notifications for upcoming birthdays"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview notifications without sending",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Send even if already notified today",
        )
        parser.add_argument(
            "--days-ahead",
            type=int,
            default=3,
            help="How many days before birthday to notify (default: 3)",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        force = options["force"]
        days_ahead = options["days_ahead"]
        if days_ahead < 0:
            raise CommandError("--days-ahead must be >= 0")

        today = timezone.localdate()
        target_date = today + timedelta(days=days_ahead)

        qs = BirthdaySubscriber.objects.filter(
            birth_date__month=target_date.month,
            birth_date__day=target_date.day,
        ).order_by("first_name", "last_name")

        if not force:
            qs = qs.exclude(last_birthday_notified_on=today)

        subscribers = list(qs)
        if not subscribers:
            self.stdout.write(
                self.style.SUCCESS(
                    f"No birthdays to notify for {target_date.strftime('%d.%m')} (days ahead: {days_ahead})."
                )
            )
            return

        lines = [
            f"🎉 Через {days_ahead} дн. день рождения у гостей Русского Ранчо ({target_date.strftime('%d.%m')}):",
            "",
        ]
        for item in subscribers:
            age = target_date.year - item.birth_date.year
            lines.append(
                f"• {item.first_name} {item.last_name} — {item.birth_date.strftime('%d.%m.%Y')} ({age} лет), {item.phone}"
            )

        message = "\n".join(lines)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: message preview"))
            self.stdout.write(message)
            return

        ok, details = send_telegram_message(message)
        if not ok:
            raise CommandError(f"Failed to send Telegram message: {details}")

        with transaction.atomic():
            for item in subscribers:
                item.last_birthday_notified_on = today
                item.save(update_fields=["last_birthday_notified_on", "updated_at"])

        self.stdout.write(
            self.style.SUCCESS(f"Sent birthday notification for {len(subscribers)} subscriber(s).")
        )
