from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from siteshop import settings
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
    extra_context = {"title": "Профиль пользователя",
                     "default_user_image": settings.DEFAULT_USER_IMAGE,
                     "default_item_image": settings.DEFAULT_ITEM_IMAGE
                     }

    def get_success_url(self):
        return reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


# class ListRulesAPI(generics.ListAPIView):
#     queryset = AccessRoleRule.objects.all()
#     serializer_class = AccessRoleRuleSerializer
#     permission_classes = [IsAdminUser]


# class UpdateRuleAPI(generics.RetrieveUpdateAPIView):
#     queryset = AccessRoleRule.objects.all()
#     serializer_class = AccessRoleRuleSerializer
#     permission_classes = [IsAdminUser]


# class AboutApi(View):
#     def get(self, request):
#         return render(request, 'users/about_api.html', {"title": "Про API"})
