# Generated by Django 5.1 on 2024-09-21 13:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chat', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='blocklist',
            name='blocked_by',
            field=models.ForeignKey(help_text='User who blocked the user.', on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blocklist',
            name='user',
            field=models.ForeignKey(blank=True, help_text='User who is blocked.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocked_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatroom',
            name='creator',
            field=models.ForeignKey(blank=True, help_text='User who created this chat room.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='creator_of_chat_rooms', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatroominvitation',
            name='chat_room',
            field=models.ForeignKey(help_text='Chat room for which the invitation is sent.', on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='chat.chatroom'),
        ),
        migrations.AddField(
            model_name='chatroominvitation',
            name='receiver',
            field=models.ForeignKey(help_text='User who is invited to the chat room.', on_delete=django.db.models.deletion.CASCADE, related_name='chat_room_invitations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatroominvitation',
            name='sender',
            field=models.ForeignKey(help_text='User who sent the invitation to the chat room.', on_delete=django.db.models.deletion.CASCADE, related_name='chat_room_invitations_sent', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatroommembership',
            name='chat_room',
            field=models.ForeignKey(help_text='Chat room in which the user is a member.', on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='chat.chatroom'),
        ),
        migrations.AddField(
            model_name='chatroommembership',
            name='user',
            field=models.ForeignKey(help_text='User who is a member of the chat room.', on_delete=django.db.models.deletion.CASCADE, related_name='chat_room_memberships', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blocklist',
            name='member_ship',
            field=models.ForeignKey(blank=True, help_text='User who is blocked in the chat room.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocked_users', to='chat.chatroommembership'),
        ),
        migrations.AddField(
            model_name='message',
            name='attachment',
            field=models.ForeignKey(blank=True, help_text='Attachment associated with the message, if any.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.attachment'),
        ),
        migrations.AddField(
            model_name='message',
            name='chat_room',
            field=models.ForeignKey(help_text='Chat room in which the message was sent.', on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatroom'),
        ),
        migrations.AddField(
            model_name='message',
            name='read_by',
            field=models.ManyToManyField(blank=True, help_text='Users who have read the message.', related_name='read_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='reply_to',
            field=models.ForeignKey(blank=True, help_text='The message to which this message is a reply, if any.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='chat.message'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(help_text='User who sent the message.', on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='messagereaction',
            name='message',
            field=models.ForeignKey(help_text='Message that received the reaction.', on_delete=django.db.models.deletion.CASCADE, related_name='message_reactions', to='chat.message'),
        ),
        migrations.AddField(
            model_name='messagereaction',
            name='user',
            field=models.ForeignKey(help_text='User who reacted to the message.', on_delete=django.db.models.deletion.CASCADE, related_name='user_reactions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='chatroominvitation',
            constraint=models.UniqueConstraint(fields=('chat_room', 'receiver', 'sender'), name='unique_chat_room_invitation'),
        ),
        migrations.AddConstraint(
            model_name='chatroommembership',
            constraint=models.UniqueConstraint(fields=('user', 'chat_room'), name='unique_user_chat_room_membership'),
        ),
        migrations.AddConstraint(
            model_name='blocklist',
            constraint=models.UniqueConstraint(fields=('user', 'blocked_by'), name='unique_blocked_user'),
        ),
        migrations.AddConstraint(
            model_name='messagereaction',
            constraint=models.UniqueConstraint(fields=('user', 'message'), name='unique_user_message_reaction'),
        ),
    ]
