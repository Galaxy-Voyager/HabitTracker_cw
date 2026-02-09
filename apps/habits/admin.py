from django.contrib import admin
from .models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'time', 'place',
                    'is_pleasant', 'is_public', 'periodicity')
    list_filter = ('is_pleasant', 'is_public', 'periodicity', 'user')
    search_fields = ('action', 'place', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'action', 'place', 'time')
        }),
        ('Настройки привычки', {
            'fields': ('is_pleasant', 'related_habit', 'periodicity',
                       'day_of_week', 'reward', 'execution_time')
        }),
        ('Видимость', {
            'fields': ('is_public',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    list_display = ('habit', 'completed_at', 'is_completed')
    list_filter = ('is_completed', 'completed_at')
    readonly_fields = ('completed_at',)
