from django.db.models.fields import json
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView
# from users.serializers import AccessRoleRuleSerializer
# from users.mixins import MyPermissionMixin
from siteshop import settings
from .forms import ProfileUserForm, RegisterUserForm, LoginForm
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.forms.models import model_to_dict
from rest_framework import generics
from rest_framework.permissions import IsAdminUser


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


# class DeleteUser(View):
#     def get(self, request):
#         return render(request, 'users/delete_confirm.html', {
#             'title': 'Удаление аккаунта'
#         })

#     def post(self, request):
#         response = redirect('home')
#         response.delete_cookie('sessionid')
#         messages.success(request, 'Ваш аккаунт был успешно удалён.')
#         return response


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
