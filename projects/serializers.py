from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project, Task, Comment, ActivityLog

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(
        source='created_by.email',
        read_only=True
    )

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description',
            'created_by_email', 'created_at'
        )
        read_only_fields = ('created_by_email', 'created_at')


class TaskSerializer(serializers.ModelSerializer):
    assignee_email = serializers.EmailField(
        source='assignee.email',
        read_only=True
    )
    created_by_email = serializers.EmailField(
        source='created_by.email',
        read_only=True
    )
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'description', 'status',
            'priority', 'assignee_id', 'assignee_email',
            'created_by_email', 'due_date',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'assignee_email', 'created_by_email',
            'created_at', 'updated_at'
        )


class CommentSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(
        source='author.email',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'body', 'author_email', 'created_at')
        read_only_fields = ('author_email', 'created_at')


class ActivityLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(
        source='actor.email',
        read_only=True
    )

    class Meta:
        model = ActivityLog
        fields = (
            'id', 'actor_email', 'action',
            'old_value', 'new_value', 'timestamp'
        )