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


class AdminModeratorAuthorPermission(permissions.BasePermission):
    def has_permission(self, request, view):

        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user and
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            if (request.user.is_staff or request.user.role == 'admin' or
                    request.user.role == 'moderator' or
                    obj.author == request.user or
                    request.method == 'POST' and request.user.is_authenticated):
                return True
        elif request.method in permissions.SAFE_METHODS:
            return True