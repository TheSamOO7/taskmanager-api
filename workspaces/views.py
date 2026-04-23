from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Workspace, WorkspaceMember
from .serializers import (
    WorkspaceSerializer,
    WorkspaceMemberSerializer,
    InviteMemberSerializer
)

User = get_user_model()


class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only return workspaces the logged-in user belongs to
        return Workspace.objects.filter(
            members__user=self.request.user
        )


class WorkspaceDetailView(generics.RetrieveAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Workspace.objects.filter(
            members__user=self.request.user
        )


class InviteMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        workspace = get_object_or_404(Workspace, pk=pk)

        # only admins can invite members
        membership = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=request.user,
            role=WorkspaceMember.Role.ADMIN
        ).first()

        if not membership:
            return Response(
                {'detail': 'Only admins can invite members.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = InviteMemberSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            role = serializer.validated_data['role']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'No user found with this email.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if WorkspaceMember.objects.filter(workspace=workspace, user=user).exists():
                return Response(
                    {'detail': 'User is already a member.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            WorkspaceMember.objects.create(
                workspace=workspace,
                user=user,
                role=role
            )

            return Response(
                {'detail': f'{email} added as {role}.'},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceMemberListView(generics.ListAPIView):
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        workspace = get_object_or_404(Workspace, pk=self.kwargs['pk'])
        return WorkspaceMember.objects.filter(workspace=workspace)