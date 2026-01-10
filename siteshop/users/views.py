from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from siteshop import settings
from shop.models import Currency, Order, RankCategory
from .forms import ProfileUserForm, RegisterUserForm, LoginForm
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect


class LoginUser(LoginView):
    form_class = LoginForm
    template_name = 'users/login.html'
    extra_context = {"title": "Авторизация"}


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("users:login"))


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "users/register.html"
    extra_context = {"title": "Регистрация"}
    success_url = reverse_lazy("users:login")


class ProfileUser(UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = "users/profile.html"
    extra_context = {
        "title": "Профиль пользователя",
        "default_user_image": settings.DEFAULT_USER_IMAGE,
        "default_item_image": settings.DEFAULT_ITEM_IMAGE,
    }

    def get_success_url(self):
        return reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()

        total_spent = user.get_total_spent()
        current_rank = RankCategory.objects.filter(
            min_total__lte=total_spent
        ).order_by('-min_total').first()

        if current_rank:
            next_rank = RankCategory.objects.filter(
                min_total__gt=total_spent
            ).order_by('min_total').first()

            if next_rank:
                current_min, next_min = float(
                    current_rank.min_total), float(next_rank.min_total)
                progress = ((total_spent - current_min) / (next_min - current_min) * 100
                            if (next_min - current_min) > 0 else 0)
                context['rank_progress'] = {
                    'current_rank': current_rank,
                    'next_rank': next_rank,
                    'total_spent': total_spent,
                    'progress_percent': min(100, max(0, progress)),
                    'needed': max(0, next_min - total_spent),
                    'is_max_rank': False
                }
            else:
                context['rank_progress'] = {
                    'current_rank': current_rank,
                    'next_rank': None,
                    'total_spent': total_spent,
                    'progress_percent': 100,
                    'needed': 0,
                    'is_max_rank': True
                }

        context['user_items'] = user.items.all().select_related('currency')

        return context
