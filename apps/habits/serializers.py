from rest_framework import serializers
from .models import Habit, HabitCompletion
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'telegram_chat_id')


class HabitSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

    def validate(self, data):
        # Проверка на связанную привычку и вознаграждение
        if data.get('related_habit') and data.get('reward'):
            raise serializers.ValidationError(
                "Нельзя одновременно связанную привычку и вознаграждение."
            )

        # Проверка времени выполнения
        if data.get('execution_time', 120) > 120:
            raise serializers.ValidationError(
                "Время выполнения не должно превышать 120 секунд."
            )

        # Проверка для приятной привычки
        if data.get('is_pleasant', False):
            if data.get('reward'):
                raise serializers.ValidationError(
                    "У приятной привычки не может быть вознаграждения."
                )
            if data.get('related_habit'):
                raise serializers.ValidationError(
                    "У приятной привычки не может быть связанной привычки."
                )

        # Проверка связанной привычки
        related_habit = data.get('related_habit')
        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError(
                "Связанные привычки могут быть только приятными."
            )

        return data


class HabitCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitCompletion
        fields = '__all__'
        read_only_fields = ('completed_at',)


class PublicHabitSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Habit
        fields = ('id', 'user', 'place', 'time', 'action',
                  'periodicity', 'execution_time', 'created_at')
        read_only_fields = fields
