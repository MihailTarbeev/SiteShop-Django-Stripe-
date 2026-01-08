from django.urls import path
from . import views


urlpatterns = [
    path('', views.PeopleHome.as_view(), name='home'),
    path('category/<slug:cat_slug>/',
         views.ShopCategory.as_view(), name='category'),
    path('item/<slug:item_slug>/', views.ShowItem.as_view(), name='item'),
    path('item/<slug:slug>/edit/', views.UpdateItem.as_view(), name='edit_item'),
    path('add_item/', views.AddItem.as_view(), name='add_item'),
    path('delete_item/<slug:slug>/',
         views.DeletePage.as_view(), name='delete_item'),
    path('create-checkout-session/',
         views.create_session, name='create_session'),
    path('create_session_success/',
         views.create_session_success, name='create_session_success'),
    path('api/v1/tax-rates/', views.stripe_tax_rates, name='tax-rates'),
]
