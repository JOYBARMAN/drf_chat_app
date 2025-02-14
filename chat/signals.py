# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.cache import cache

# from chat.models import Message

# from shared.cache_key import get_chat_room_messages_cache_key


# @receiver(post_save, sender=Message)
# def message_post_save(sender, instance, created, **kwargs):
#     # Handle the message post save and update the read_by field
#     if created:
#         cache_key = get_chat_room_messages_cache_key(instance.chat_room.uid)
#         latest_data = (
#             instance.__class__.get_active_instance()
#             .filter(chat_room__uid=instance.chat_room.uid)
#             .select_related(
#                 "sender",
#                 "attachment",
#                 "reply_to__sender",
#                 "reply_to__attachment",
#             )
#             .prefetch_related(
#                 "read_by",
#                 "message_reactions__user",
#             )
#             .order_by("-created_at")
#         )

#         # Set new data in cache
#         cache.set(cache_key, latest_data)
