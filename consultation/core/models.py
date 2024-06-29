from django.db import models
from schedule.models import Event


class TGUser(models.Model):
    user_id = models.CharField(verbose_name='Телеграм id', max_length=100, unique=True)
    username = models.CharField(verbose_name='Ник телеграм', max_length=100, null=True, blank=True)
    name = models.CharField(verbose_name='Имя', max_length=100, null=True, blank=True)
    phone = models.CharField(verbose_name='Номер телефона', max_length=25, null=True, blank=True)
    age = models.IntegerField(verbose_name='Возраст', null=True, blank=True)
    height = models.IntegerField(verbose_name='Рост (см)', null=True, blank=True)
    weight = models.IntegerField(verbose_name='Вес (кг)', null=True, blank=True)
    budget = models.CharField(verbose_name='Бюджет годовой', max_length=100, null=True, blank=True)
    questionnaire_completed = models.BooleanField(verbose_name='Анкета заполнена', default=False)
    curr_input = models.CharField(verbose_name='Телеграм id', max_length=100, null=True, blank=True, default=None)
    consultation = models.ForeignKey(Event, verbose_name='Консультация', on_delete=models.SET_NULL, related_name='customer', null=True, blank=True, default=None)
    
    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'Клиенты'
    
    def __str__(self):
        if self.name:
            return self.name
        return 'Имя не указано'


class Budget(models.Model):
    amount = models.CharField(verbose_name='Бюджет', max_length=100, unique=True)
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        verbose_name = 'бюджет'
        verbose_name_plural = 'Годовые бюджеты'
        ordering = ('my_order',)
    
    def __str__(self):
        return str(self.amount)


class TelegramText(models.Model):
    slug = models.CharField(verbose_name='Идентификатор', max_length=100, unique=True)
    text = models.TextField(verbose_name='Текст', max_length=4096)

    class Meta:
        verbose_name = 'текст'
        verbose_name_plural = 'Текстовое наполнение'
    
    def __str__(self):
        return self.slug