from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Habit

User = get_user_model()


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            place='Дома',
            time='09:00:00',
            action='Читать книгу',
            execution_time=60,
            is_public=True
        )
        self.assertEqual(habit.action, 'Читать книгу')
        self.assertEqual(habit.user.username, 'testuser')

    def test_pleasant_habit_no_reward(self):
        with self.assertRaises(Exception):
            Habit.objects.create(
                user=self.user,
                place='Дома',
                time='10:00:00',
                action='Принять ванну',
                is_pleasant=True,
                reward='Шоколад',
                execution_time=90
            )


class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            telegram_chat_id='123456'
        )
        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            'place': 'Парк',
            'time': '08:00:00',
            'action': 'Утренняя пробежка',
            'execution_time': 90,
            'is_public': True
        }

    def test_create_habit(self):
        response = self.client.post('/api/habits/', self.habit_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['action'], 'Утренняя пробежка')

    def test_list_habits(self):
        Habit.objects.create(user=self.user, **self.habit_data)
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем пагинацию
        self.assertIn('results', response.data)

    def test_public_habits(self):
        # Создаем публичную привычку
        Habit.objects.create(user=self.user, **self.habit_data)

        # Создаем другого пользователя
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.force_authenticate(user=other_user)

        # Проверяем доступ к публичным привычкам
        response = self.client.get('/api/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_complete_habit(self):
        habit = Habit.objects.create(user=self.user, **self.habit_data)
        response = self.client.post(f'/api/habits/{habit.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class AuthAPITest(APITestCase):
    def test_register_user(self):
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        }
        response = self.client.post('/api/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_token(self):
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/token/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
