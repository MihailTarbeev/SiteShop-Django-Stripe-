from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from siteshop import settings
from .models import CartItem, Item, Cart
from .mixins import UserOwnerMixin
import stripe
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
import stripe
from django.conf import settings
from .forms import ItemForm, AddToCartForm
from django.contrib.auth.decorators import login_required


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
        context['item_in_cart'] = False
        context['cart_quantity'] = 0

        if self.request.user.is_authenticated:
            cart_item = CartItem.objects.filter(
                cart__user=self.request.user,
                item=context['item']
            ).first()

            if cart_item:
                context['item_in_cart'] = True
                context['cart_quantity'] = cart_item.quantity

        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Item, slug=self.kwargs[self.slug_url_kwarg], is_available=True)


class UpdateItem(LoginRequiredMixin, UserOwnerMixin, UpdateView):
    form_class = ItemForm
    model = Item
    template_name = 'shop/edit_item.html'
    extra_context = {"title": "Редактирование",
                     'default_image': settings.DEFAULT_ITEM_IMAGE}
    context_object_name = "item"


class AddItem(LoginRequiredMixin, CreateView):
    form_class = ItemForm
    model = Item
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


def create_session(request, item_slug):
    item = get_object_or_404(Item, slug=item_slug, is_available=True)
    taxes = item.taxes.all()

    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': item.currency,
                'product_data': {
                    'name': item.name,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': 1,
            'tax_rates': [tax.stripe_tax_id for tax in taxes]
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/create_session_success',
    )

    return redirect(session.url, code=303)


def create_session_success(request):
    return render(request, "shop/success.html")


@api_view(['GET'])
def stripe_tax_rates(request):
    """
    GET-параметры:
    limit = 50 (по умолчанию)
    starting_after - id rate, с которого начинать
    ending_before - id rate, по который заканчивать
    Сортировка по увеличению времени создания
    """
    limit = int(request.GET.get('limit', 50))
    starting_after = request.GET.get('starting_after')
    ending_before = request.GET.get('ending_before')
    try:
        tax_rates = stripe.TaxRate.list(
            limit=limit, starting_after=starting_after, ending_before=ending_before)

        for tax_rate in tax_rates:
            dt_object = datetime.fromtimestamp(
                tax_rate["created"], tz=timezone.utc)
            tax_rate["created_UTC"] = dt_object.strftime(
                '%Y-%m-%d %H:%M:%S UTC')

        return Response({'data': tax_rates.data, "count": len(tax_rates)})
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
def stripe_coupons(request):
    """
    GET-параметры:
    limit = 50 (по умолчанию)
    starting_after - id rate, с которого начинать
    ending_before - id rate, по который заканчивать
    Сортировка по увеличению времени создания
    """
    limit = int(request.GET.get('limit', 50))
    starting_after = request.GET.get('starting_after')
    ending_before = request.GET.get('ending_before')
    try:
        tax_rates = stripe.Coupon.list(
            limit=limit, starting_after=starting_after, ending_before=ending_before)

        for tax_rate in tax_rates:
            dt_object = datetime.fromtimestamp(
                tax_rate["created"], tz=timezone.utc)
            tax_rate["created_UTC"] = dt_object.strftime(
                '%Y-%m-%d %H:%M:%S UTC')

        return Response({'data': tax_rates.data, "count": len(tax_rates)})
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=400)


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.select_related('item').all()
    total_price = cart.get_total_price()
    currencies = set(cart_item.item.currency for cart_item in cart_items)
    total_quantity = cart.get_total_quantity()

    context = {
        'cart': cart,
        'cart_items': cart_items,
        "total_price": total_price,
        "total_quantity": total_quantity,
        'title': 'Корзина',
        'has_multiple_currencies': len(currencies) > 1,
        'currencies': currencies,
    }

    return render(request, 'shop/cart.html', context)


def clear_cart(request):
    pass


@login_required
def add_to_cart(request, item_slug):
    item = get_object_or_404(Item, slug=item_slug, is_available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    form = AddToCartForm(request.POST)

    if form.is_valid():
        quantity = form.cleaned_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item=item,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

    return redirect('item', item_slug=item_slug)


@login_required
def remove_from_cart(request, item_slug):
    item = get_object_or_404(Item, slug=item_slug)

    cart = Cart.objects.get(user=request.user)
    if cart:
        cart_item = cart.items.get(item=item)
        if cart_item:
            cart_item.delete()

    return redirect('view_cart')


@login_required
def update_cart_item(request, item_slug):
    item = get_object_or_404(Item, slug=item_slug)

    form = AddToCartForm(request.POST)

    if form.is_valid():
        quantity = form.cleaned_data['quantity']

        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_item = cart.items.filter(item=item).first()
            if cart_item:
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()

                else:
                    cart_item.delete()

    return redirect('view_cart')
