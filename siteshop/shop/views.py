from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from siteshop import settings
from .models import Item
from .mixins import UserOwnerMixin
import stripe
from rest_framework.decorators import api_view
from rest_framework.response import Response


from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe
from django.conf import settings


@api_view(['GET'])
def stripe_tax_rates(request):
    """
    GET-параметры:
    limit = 50 (по умолчанию)
    starting_after - id rate, с которого начинать
    ending_before - id rate, по который заканчивать
    Сортировка по увеличению времени создания
    """
    try:
        tax_rates = stripe.TaxRate.list(**{
            'limit': int(request.GET.get('limit', 50)),
            'starting_after': request.GET.get('starting_after'),
            'ending_before': request.GET.get('ending_before')
        })
        return Response({'data': tax_rates.data, "count": len(tax_rates)})
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=400)


class PeopleHome(ListView):
    model = Item
    template_name = "shop/index.html"
    context_object_name = "items"
    extra_context = {"title": "Главная страница", "category_selected": 0,
                     "default_image": settings.DEFAULT_ITEM_IMAGE}

    def get_queryset(self):
        return Item.published.all().select_related("category")


class ShopCategory(ListView):
    template_name = 'shop/index.html'
    context_object_name = "items"
    allow_empty = False

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = context["item"].name
        context['default_image'] = settings.DEFAULT_ITEM_IMAGE
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Item, slug=self.kwargs[self.slug_url_kwarg], is_available=True)


class UpdateItem(LoginRequiredMixin, UserOwnerMixin, UpdateView):
    model = Item
    fields = ["image", "name", "price", "description",
              "is_available", "category", "slug"]
    template_name = 'shop/edit_item.html'
    extra_context = {"title": "Редактирование",
                     'default_image': settings.DEFAULT_ITEM_IMAGE}
    context_object_name = "item"


class AddItem(LoginRequiredMixin, CreateView):
    model = Item
    fields = ["image", "name", "price", "description",
              "is_available", "category", "slug"]
    template_name = 'shop/addpage.html'
    extra_context = {"title": 'Добавить товар'}

    def form_valid(self, form):
        w = form.save(commit=False)
        w.owner = self.request.user
        return super().form_valid(form)


class DeletePage(LoginRequiredMixin, UserOwnerMixin, DeleteView):
    model = Item
    context_object_name = "item"
    success_url = reverse_lazy("home")
    extra_context = {"title": "Удаление товара",
                     'default_image': settings.DEFAULT_ITEM_IMAGE}


def create_session(request):
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'T-shirt',
                },
                'unit_amount': 2000,
            },
            'quantity': 1,
            'tax_rates': ["txr_1SnCZvKpfYmXuwND0q23shWZ",]
        },
            {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'T-shirt',
                },
                'unit_amount': 2000,
            },
            'quantity': 1,
            'tax_rates': ["txr_1SnCZvKpfYmXuwND0q23shWZ",]
        },],
        # discounts=[{"coupon": "ded-moroz"}],
        tax_id_collection={'enabled': True},
        # tax_rates={"type": "eu_vat"},
        mode='payment',
        # allow_promotion_codes=True,
        success_url='http://127.0.0.1:8000/create_session_success',
    )

    return redirect(session.url, code=303)


def create_session_success(request):
    return render(request, "shop/success.html")
