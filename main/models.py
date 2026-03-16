from django.db import models
from django.contrib.auth.models import User


class BirthdaySubscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")
    first_name = models.CharField("Имя", max_length=80)
    last_name = models.CharField("Фамилия", max_length=80)
    phone = models.CharField("Телефон", max_length=32, unique=True)
    birth_date = models.DateField("Дата рождения")
    last_birthday_notified_on = models.DateField("Последнее уведомление о дне рождения", null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Подписчик на поздравления"
        verbose_name_plural = "Подписчики на поздравления"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone})"
