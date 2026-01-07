from django.core.exceptions import PermissionDenied


class UserOwnerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied
        return super(UserOwnerMixin, self).dispatch(request, *args, **kwargs)
