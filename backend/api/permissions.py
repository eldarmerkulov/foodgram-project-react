from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in SAFE_METHODS
                )

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author
                or request.user.is_admin)
