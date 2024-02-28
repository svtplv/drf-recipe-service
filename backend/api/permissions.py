from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)


class IsAuthorStaffOrReadOnly(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated and any((
                request.user.is_staff,
                obj.author == request.user
            ))
        )
