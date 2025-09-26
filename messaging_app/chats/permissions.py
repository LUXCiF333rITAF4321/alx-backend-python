from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsParticipantOfConversation(BasePermission):
    """
    Permission to check if user is a participant in the conversation.
    Allow only authenticated users to access the api.
    Allow only participants in a conversation to send, view, update and delete messages.
    """
    
    def has_permission(self, request, view):
        """
        Only allow authenticated users to access the API
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Allow only participants in a conversation to send, view, update and delete messages
        """
        # For Message objects, check if user is participant in the conversation
        if hasattr(obj, 'conversation'):  # This is a Message object
            return request.user in obj.conversation.participants.all()
        
        # For Conversation objects, check if user is a participant
        elif hasattr(obj, 'participants'):  # This is a Conversation object
            return request.user in obj.participants.all()
        
        return False


class IsParticipantInConversation(BasePermission):
    """
    Permission to check if user is a participant in the conversation
    """
    
    def has_permission(self, request, view):
        """
        Only allow authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is a participant in the conversation
        """
        return request.user in obj.participants.all()


class IsMessageSenderOrParticipant(BasePermission):
    """
    Permission to check if user is the sender of the message or participant in conversation
    """
    
    def has_permission(self, request, view):
        """
        Only allow authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        For messages, check if user is the sender or participant in the conversation
        """
        if hasattr(obj, 'sender'):  # This is a Message object
            return (
                request.user == obj.sender or 
                request.user in obj.conversation.participants.all()
            )
        return False


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission to only allow owners of an object to edit it
    """
    
    def has_permission(self, request, view):
        """
        Only allow authenticated users
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Read permissions for any authenticated user.
        Write permissions only to the owner.
        """
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions only to the owner
        if hasattr(obj, 'sender'):  # Message object
            return obj.sender == request.user
        elif hasattr(obj, 'participants'):  # Conversation object
            return request.user in obj.participants.all()
        
        return False
