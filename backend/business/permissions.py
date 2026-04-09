from rest_framework.permissions import BasePermission, SAFE_METHODS


class RolePermission(BasePermission):
    allowed_roles = set()
    read_only_roles = set()

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        role_code = getattr(user, "role_code", None)
        if request.method in SAFE_METHODS:
            return role_code in self.allowed_roles.union(self.read_only_roles)
        return role_code in self.allowed_roles


class AdminOnly(RolePermission):
    allowed_roles = {"ADMIN"}


class AdminOrStoreKeeper(RolePermission):
    allowed_roles = {"ADMIN", "STORE_KEEPER"}
    read_only_roles = {"CASHIER"}


class AdminOrCashier(RolePermission):
    allowed_roles = {"ADMIN", "CASHIER"}
    read_only_roles = {"STORE_KEEPER"}


class AuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
