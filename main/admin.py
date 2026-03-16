from django.contrib import admin
from .models import BirthdaySubscriber


@admin.register(BirthdaySubscriber)
class BirthdaySubscriberAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "user", "birth_date", "last_birthday_notified_on", "created_at")
    search_fields = ("first_name", "last_name", "phone")
    list_filter = ("birth_date", "last_birthday_notified_on", "created_at")
