from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('login/', views.LoginUser.as_view(), name='login'),
    # path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),
    # path('delete/', views.DeleteUser.as_view(), name='delete_user'),
    # path('api/v1/rules/', views.ListRulesAPI.as_view(), name='api_rules'),
    # path('api/v1/rules/<int:pk>/', views.UpdateRuleAPI.as_view(),
    #      name='api_rule_detail'),
    # path('about_api', views.AboutApi.as_view(), name='about_api'),
]
