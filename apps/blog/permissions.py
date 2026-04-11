# Django Rest Framework modules
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Anyone can read (GET)
    - Only owners can edit or delete (PATCH, PUT, DELETE)
    """

    def has_object_permission(self, request: Request, view: APIView, obj: object) -> bool:
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.author == request.user
