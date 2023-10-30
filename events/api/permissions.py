from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAdminUser)


class ReadOnly(BasePermission):
    """
    Класс разрешений, позволяющий считывать данные только прошедшим проверку
    подлинности пользователям.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.method in SAFE_METHODS


class AdminOnly(BasePermission):
    """
    Класс разрешений, который позволяет только аутентифицированным
    администраторам выполнять операции записи (добавление, изменение,
    удаление).
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and
                IsAdminUser().has_permission(request, view))
