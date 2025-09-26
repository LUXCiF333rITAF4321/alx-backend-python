from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer, 
    ConversationListSerializer, 
    MessageSerializer,
    UserSerializer
)
from .permissions import (
    IsParticipantInConversation,
    IsMessageSenderOrParticipant,
    IsOwnerOrReadOnly
)

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling conversation operations
    """
    permission_classes = [IsAuthenticated, IsParticipantInConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return conversations where the current user is a participant
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages')
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action
        """
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def get_permissions(self):
        """
        Get permissions based on action
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsParticipantInConversation]
        return [permission() for permission in permission_classes]
    
    def list(self, request):
        """
        List all conversations for the authenticated user
        """
        queryset = self.get_queryset()
        serializer = ConversationListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific conversation with all messages
        """
        conversation = get_object_or_404(
            self.get_queryset(), 
            conversation_id=pk
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        """
        Create a new conversation
        """
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            # Add the current user to participants if not already included
            participants_ids = serializer.validated_data.get('participants_ids', [])
            if request.user.user_id not in participants_ids:
                participants_ids.append(request.user.user_id)
                serializer.validated_data['participants_ids'] = participants_ids
            
            conversation = serializer.save()
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """
        Update conversation participants
        """
        conversation = get_object_or_404(
            self.get_queryset(), 
            conversation_id=pk
        )
        serializer = ConversationSerializer(conversation, data=request.data, partial=True)
        if serializer.is_valid():
            conversation = serializer.save()
            return Response(
                ConversationSerializer(conversation).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        Delete a conversation (only if user is a participant)
        """
        conversation = get_object_or_404(
            self.get_queryset(), 
            conversation_id=pk
        )
        conversation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to an existing conversation
        """
        conversation = get_object_or_404(
            self.get_queryset(), 
            conversation_id=pk
        )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response(
                {'message': 'Participant added successfully'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from a conversation
        """
        conversation = get_object_or_404(
            self.get_queryset(), 
            conversation_id=pk
        )
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            return Response(
                {'message': 'Participant removed successfully'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling message operations
    """
    permission_classes = [IsAuthenticated, IsMessageSenderOrParticipant]
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conversation', 'sender', 'sent_at']
    search_fields = ['message_body', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['sent_at']
    ordering = ['sent_at']
    
    def get_queryset(self):
        """
        Return messages from conversations where the user is a participant
        """
        user_conversations = Conversation.objects.filter(
            participants=self.request.user
        )
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation')
    
    def get_permissions(self):
        """
        Get permissions based on action
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticated, IsMessageSenderOrParticipant]
        return [permission() for permission in permission_classes]
    
    def list(self, request):
        """
        List messages, optionally filtered by conversation
        """
        conversation_id = request.query_params.get('conversation_id')
        queryset = self.get_queryset()
        
        if conversation_id:
            # Filter messages by conversation
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific message
        """
        message = get_object_or_404(self.get_queryset(), message_id=pk)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        """
        Send a new message to a conversation
        """
        # Automatically set the sender to the current user
        data = request.data.copy()
        data['sender_id'] = request.user.user_id
        
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            # Verify that the user is a participant in the conversation
            conversation_id = serializer.validated_data['conversation'].conversation_id
            conversation = get_object_or_404(
                Conversation.objects.filter(participants=request.user),
                conversation_id=conversation_id
            )
            
            message = serializer.save()
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """
        Update a message (only if user is the sender)
        """
        message = get_object_or_404(
            self.get_queryset().filter(sender=request.user), 
            message_id=pk
        )
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            message = serializer.save()
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """
        Delete a message (only if user is the sender)
        """
        message = get_object_or_404(
            self.get_queryset().filter(sender=request.user), 
            message_id=pk
        )
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        Custom endpoint to send a message to a conversation
        """
        conversation_id = request.data.get('conversation_id')
        message_body = request.data.get('message_body')
        
        if not conversation_id or not message_body:
            return Response(
                {'error': 'conversation_id and message_body are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify conversation exists and user is a participant
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_id,
                participants=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found or access denied'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the message
        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            message_body=message_body
        )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user operations (read-only for security)
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        """
        Return all users for participant selection
        """
        return User.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's information
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
