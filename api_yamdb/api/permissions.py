from rest_framework import permissions


class AdminOrReadOnnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            try:
                return 'admin' == request.user.role
            except AttributeError:
                return False

        return True


class Admin(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_superuser or 'admin' == request.user.role
        except AttributeError:
            return False
