from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
# from users.models import AccessRoleRule, BusinessElement
# from users.mixins import MyPermissionMixin
from siteshop import settings
from .models import Item


class PeopleHome(ListView):
    model = Item
    template_name = "shop/index.html"
    context_object_name = "items"
    extra_context = {"title": "Главная страница", "category_selected": 0,
                     "default_image": settings.DEFAULT_ITEM_IMAGE}
    # permissions_required = "Items.read_all_permission"

    def get_queryset(self):
        return Item.published.all().select_related("category")


class ShopCategory(ListView):
    template_name = 'shop/index.html'
    context_object_name = "items"
    allow_empty = False
    # permissions_required = "Items.read_all_permission"

    def get_queryset(self):
        return Item.published.filter(category__slug=self.kwargs["cat_slug"]).select_related("category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = context["items"][0].category
        context['category_selected'] = category.pk
        context['title'] = "Категория - " + category.name
        context['default_image'] = settings.DEFAULT_ITEM_IMAGE
        return context


class ShowItem(DetailView):
    model = Item
    template_name = 'shop/item.html'
    slug_url_kwarg = "item_slug"
    context_object_name = "item"
    # permission_required = "Items.read_permission"
    # check_ownership = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context["item"].name
        context['default_image'] = settings.DEFAULT_ITEM_IMAGE
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Item, slug=self.kwargs[self.slug_url_kwarg], is_available=True)


class UpdateItem(UpdateView):
    # permission_required = "Items.update_permission"
    # check_ownership = True

    model = Item
    fields = ["image", "name", "price", "description",
              "is_available", "category", "slug"]
    template_name = 'shop/edit_item.html'
    extra_context = {"title": "Редактирование",
                     'default_image': settings.DEFAULT_ITEM_IMAGE}
    context_object_name = "item"


class AddItem(CreateView):
    model = Item
    fields = ["image", "name", "price", "description",
              "is_available", "category", "slug"]
    template_name = 'shop/addpage.html'
    extra_context = {"title": 'Добавить товар'}
    # permission_required = "Items.create_permission"

    def form_valid(self, form):
        w = form.save(commit=False)
        w.owner = self.request.user
        return super().form_valid(form)


class DeletePage(DeleteView):
    # permission_required = "Items.delete_permission"
    # check_ownership = True
    model = Item
    context_object_name = "item"
    success_url = reverse_lazy("home")
    extra_context = {"title": "Удаление товара",
                     'default_image': settings.DEFAULT_ITEM_IMAGE}
