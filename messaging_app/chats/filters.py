import django_filters
from .models import Message


class MessageFilter(django_filters.FilterSet):
    # Filter by sender user_id
    sender = django_filters.NumberFilter(field_name="sender__user_id", lookup_expr="exact")
    # Filter by conversation_id
    conversation = django_filters.NumberFilter(field_name="conversation__conversation_id", lookup_expr="exact")
    # Filter by date range
    sent_after = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="gte")
    sent_before = django_filters.DateTimeFilter(field_name="sent_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ["sender", "conversation", "sent_after", "sent_before"]
