from django.core.exceptions import PermissionDenied
from .models import Cart


class UserOwnerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != self.request.user:
            raise PermissionDenied
        return super(UserOwnerMixin, self).dispatch(request, *args, **kwargs)


class CartMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        if request.user.is_authenticated:
            self.cart, created = Cart.objects.get_or_create(user=request.user)
            self.cart_created = created
