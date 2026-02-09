from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Habit(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Ежедневно'),
        ('weekly', 'Еженедельно'),
    ]

    DAYS_OF_WEEK = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )
    place = models.CharField(
        max_length=255,
        verbose_name='Место выполнения',
        help_text='Место выполнения привычки'
    )
    time = models.TimeField(
        verbose_name='Время выполнения',
        help_text='Время выполнения привычки'
    )
    action = models.CharField(
        max_length=500,
        verbose_name='Действие',
        help_text='Действие привычки'
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Признак приятной привычки'
    )
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанная привычка',
        help_text='Связанная привычка'
    )
    periodicity = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
        default='daily',
        verbose_name='Периодичность'
    )
    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        null=True,
        blank=True,
        verbose_name='День недели'
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Вознаграждение'
    )
    execution_time = models.PositiveIntegerField(
        default=120,
        verbose_name='Время на выполнение (секунды)',
        help_text='Время на выполнение (макс. 120 сек.)'
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Признак публичности'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        errors = {}

        # Валидация 1
        if self.related_habit and self.reward:
            msg = 'Нельзя одновременно связанную привычку и вознаграждение.'
            errors['reward'] = msg
            errors['related_habit'] = msg

        # Валидация 2
        if self.execution_time > 120:
            msg = 'Время выполнения не должно превышать 120 секунд.'
            errors['execution_time'] = msg

        # Валидация 3
        if self.related_habit and not self.related_habit.is_pleasant:
            msg = 'Связанные привычки могут быть только приятными.'
            errors['related_habit'] = msg

        # Валидация 4
        if self.is_pleasant:
            if self.reward:
                msg = 'У приятной привычки не может быть вознаграждения.'
                errors['reward'] = msg
            if self.related_habit:
                msg = 'У приятной привычки не может быть связанной привычки.'
                errors['related_habit'] = msg

        # Валидация 5
        if self.periodicity == 'weekly' and not self.day_of_week:
            msg = 'Для еженедельной привычки укажите день недели.'
            errors['day_of_week'] = msg

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        user_action = f"{self.user.username}: {self.action}"
        time_place = f" в {self.time} в {self.place}"
        return user_action + time_place

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']


class HabitCompletion(models.Model):
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='completions'
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Выполнение привычки'
        verbose_name_plural = 'Выполнения привычек'
        ordering = ['-completed_at']
