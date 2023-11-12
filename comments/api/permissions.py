from rest_framework.permissions import BasePermission

class IsObjectOwner(BasePermission):

    message = 'you do not have the permission to access the object.'

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user