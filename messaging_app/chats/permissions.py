from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsParticipantOfConversation(BasePermission):
    """
    Allow only authenticated users and only participants
    in a conversation to send, view, update and delete messages.
    """

    def has_permission(self, request, view):
        # Only authenticated users can access
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Safe methods (GET, HEAD, OPTIONS) → allow if participant
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'conversation'):  # Message object
                return request.user in obj.conversation.participants.all()
            elif hasattr(obj, 'participants'):  # Conversation object
                return request.user in obj.participants.all()
            return False

        # Write methods (POST, PUT, PATCH, DELETE) → must be participant
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            if hasattr(obj, 'conversation'):  # Message object
                return request.user in obj.conversation.participants.all()
            elif hasattr(obj, 'participants'):  # Conversation object
                return request.user in obj.participants.all()
            return False

        return False
