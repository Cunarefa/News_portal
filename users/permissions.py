from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUserOrIsAdminOrReadSelfOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS and request.user.is_authenticated:
            return True
        if request.method in ['PATCH', 'PUT']:
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj == request.user or bool(request.user.is_staff and not obj.is_superuser)





