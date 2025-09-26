from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsParticipantInConversation(BasePermission):
    """
    Permission to check if user is a participant in the conversation
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()


class IsMessageSenderOrParticipant(BasePermission):
    """
    Permission to check if user is the sender of the message or participant in conversation
    """
    
    def has_object_permission(self, request, view, obj):
        # For messages, check if user is the sender or participant in the conversation
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
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
            
        # Write permissions only to the owner
        if hasattr(obj, 'sender'):  # Message object
            return obj.sender == request.user
        elif hasattr(obj, 'participants'):  # Conversation object
            return request.user in obj.participants.all()
        
        return False
