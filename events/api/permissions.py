from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAdminUser)


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.method in SAFE_METHODS


class AdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and IsAdminUser().has_permission(request, view)
