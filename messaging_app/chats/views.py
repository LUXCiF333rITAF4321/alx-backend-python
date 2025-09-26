from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    UserSerializer,
)
from .permissions import IsParticipantOfConversation, IsOwnerOrReadOnly
from .pagination import MessagePagination
from .filters import MessageFilter


User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')

    def get_serializer_class(self):
        return ConversationListSerializer if self.action == 'list' else ConversationSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated] if self.action == 'create' else [IsParticipantOfConversation]
        return [permission() for permission in permission_classes]

    # Standard CRUD + participant management
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ConversationListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        conversation = get_object_or_404(self.get_queryset(), conversation_id=pk)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            participants_ids = serializer.validated_data.get('participants_ids', [])
            if request.user.user_id not in participants_ids:
                participants_ids.append(request.user.user_id)
                serializer.validated_data['participants_ids'] = participants_ids
            conversation = serializer.save()
            return Response(ConversationSerializer(conversation).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        conversation = get_object_or_404(self.get_queryset(), conversation_id=pk)
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not allowed to update this conversation."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ConversationSerializer(conversation, data=request.data, partial=True)
        if serializer.is_valid():
            conversation = serializer.save()
            return Response(ConversationSerializer(conversation).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        conversation = get_object_or_404(self.get_queryset(), conversation_id=pk)
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not allowed to delete this conversation."}, status=status.HTTP_403_FORBIDDEN)
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = get_object_or_404(self.get_queryset(), conversation_id=pk)
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not allowed to modify this conversation."}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response({'message': 'Participant added successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        conversation = get_object_or_404(self.get_queryset(), conversation_id=pk)
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not allowed to modify this conversation."}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            return Response({'message': 'Participant removed successfully'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsParticipantOfConversation]
    serializer_class = MessageSerializer
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['sent_at']
    ordering = ['sent_at']

    def get_queryset(self):
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations).select_related('sender', 'conversation')

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'destroy']:
            permission_classes = [IsParticipantOfConversation, IsOwnerOrReadOnly]
        else:
            permission_classes = [IsParticipantOfConversation]
        return [permission() for permission in permission_classes]

    # List messages with filters and pagination
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        message = get_object_or_404(self.get_queryset(), message_id=pk)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data.copy()
        data['sender_id'] = request.user.user_id
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            conversation_id = serializer.validated_data['conversation'].conversation_id
            conversation = get_object_or_404(Conversation.objects.filter(participants=request.user), conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response({"detail": "You are not allowed to send messages in this conversation."}, status=status.HTTP_403_FORBIDDEN)
            message = serializer.save()
            return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        message = get_object_or_404(self.get_queryset().filter(sender=request.user), message_id=pk)
        if request.user != message.sender:
            return Response({"detail": "You are not allowed to update this message."}, status=status.HTTP_403_FORBIDDEN)
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            message = serializer.save()
            return Response(MessageSerializer(message).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        message = get_object_or_404(self.get_queryset().filter(sender=request.user), message_id=pk)
        if request.user != message.sender:
            return Response({"detail": "You are not allowed to delete this message."}, status=status.HTTP_403_FORBIDDEN)
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        conversation_id = request.data.get('conversation_id')
        message_body = request.data.get('message_body')
        if not conversation_id or not message_body:
            return Response({'error': 'conversation_id and message_body are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id, participants=request.user)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found or access denied'}, status=status.HTTP_403_FORBIDDEN)
        message = Message.objects.create(sender=request.user, conversation=conversation, message_body=message_body)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
