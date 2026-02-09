from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Habit, HabitCompletion
from .serializers import HabitSerializer, HabitCompletionSerializer
from .serializers import PublicHabitSerializer
from .permissions import IsOwner


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_pleasant', 'periodicity', 'is_public']

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        habit = self.get_object()
        completion = HabitCompletion.objects.create(habit=habit)
        serializer = HabitCompletionSerializer(completion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PublicHabitListView(generics.ListAPIView):
    serializer_class = PublicHabitSerializer
    permission_classes = [AllowAny]
    queryset = Habit.objects.filter(is_public=True)
