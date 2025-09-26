from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password_hash = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 
            'username',
            'first_name', 
            'last_name', 
            'email', 
            'password_hash',
            'phone_number', 
            'role', 
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password_hash': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def create(self, validated_data):
        """
        Create and return a new User instance with encrypted password
        """
        password = validated_data.pop('password_hash')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing User instance
        """
        password = validated_data.pop('password_hash', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']

    def validate_sender_id(self, value):
        """
        Validate that the sender exists
        """
        try:
            User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender does not exist.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested messages and participants
    """
    participants = UserSerializer(many=True, read_only=True)
    participants_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participants_ids',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def validate_participants_ids(self, value):
        """
        Validate that all participants exist and there are at least 2 participants
        """
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        
        for user_id in value:
            try:
                User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with ID {user_id} does not exist.")
        
        return value

    def create(self, validated_data):
        """
        Create a new conversation with participants
        """
        participants_ids = validated_data.pop('participants_ids')
        conversation = Conversation.objects.create()
        
        # Add participants to the conversation
        participants = User.objects.filter(user_id__in=participants_ids)
        conversation.participants.set(participants)
        
        return conversation

    def update(self, instance, validated_data):
        """
        Update conversation participants
        """
        participants_ids = validated_data.pop('participants_ids', None)
        
        if participants_ids:
            participants = User.objects.filter(user_id__in=participants_ids)
            instance.participants.set(participants)
        
        return instance


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing conversations without nested messages
    """
    participants = UserSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'message_count',
            'last_message',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation
        """
        return obj.messages.count()

    def get_last_message(self, obj):
        """
        Get the last message in the conversation
        """
        last_message = obj.messages.last()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender': last_message.sender.email
            }
        return None
