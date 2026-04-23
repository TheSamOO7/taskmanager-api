from rest_framework import serializers
from django.utils.text import slugify
from .models import Workspace, WorkspaceMember


class WorkspaceSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Workspace
        fields = ('id', 'name', 'slug', 'owner_email', 'created_at')
        read_only_fields = ('slug', 'owner_email', 'created_at')

    def create(self, validated_data):
        user = self.context['request'].user
        name = validated_data['name']
        slug = slugify(name)

        # make slug unique if it already exists
        original_slug = slug
        counter = 1
        while Workspace.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        workspace = Workspace.objects.create(
            name=name,
            slug=slug,
            owner=user
        )

        # automatically add owner as admin member
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceMember.Role.ADMIN
        )

        return workspace


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ('id', 'user_email', 'user_full_name', 'role', 'joined_at')
        read_only_fields = ('user_email', 'user_full_name', 'joined_at')


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=WorkspaceMember.Role.choices,
        default=WorkspaceMember.Role.MEMBER
    )