from rest_framework import permissions


class AdminOrReadOnnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method not in permissions.SAFE_METHODS:
            try:
                return request.user.is_admin
            except AttributeError:
                return False

        return True


class Admin(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_superuser or request.user.is_admin
        except AttributeError:
            return False


class AdminModeratorAuthorPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (
                request.user.is_staff or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user)
        else:
            return bool(request.method in permissions.SAFE_METHODS)
