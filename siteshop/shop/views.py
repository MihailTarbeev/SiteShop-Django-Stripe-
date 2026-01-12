from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from siteshop import settings
from .models import CartItem, Item, Cart, Order, OrderItem, RankCategory
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
from django.contrib import messages


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

    def form_valid(self, form):
        item = self.get_object()

        if item.orderitem_set.exists():
            item.is_available = False
            item.save()

            messages.success(
                self.request,
                f'Товар "{item.name}" деактивирован (скрыт из продажи). '
                'Он сохранен в системе, так как есть связанные заказы.'
            )
        else:
            return super().form_valid(form)

        return redirect('home')


@login_required
def create_session_item(request, item_slug):
    item = get_object_or_404(Item, slug=item_slug, is_available=True)
    taxes = item.taxes.all()
    total_spent = request.user.get_total_spent()
    current_rank = RankCategory.objects.filter(
        min_total__lte=total_spent
    ).order_by('-min_total').first()
    discount = current_rank.discount
    coupon = discount.stripe_coupon_id if discount.is_active else None

    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': item.currency.code,
                    'product_data': {
                        'name': item.name,
                    },
                    'unit_amount': int(item.price * 100),
                },
                'quantity': 1,
                'tax_rates': [tax.stripe_tax_id for tax in taxes]
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('create_session_success')
            ) + '?session_id={CHECKOUT_SESSION_ID}',
            discounts=[
                {'coupon': f"{current_rank.discount.stripe_coupon_id}"}] if coupon else None
        )

        order = Order.objects.create(
            user=request.user,
            stripe_session_id=session.id,
            total_amount=item.price,
            currency=item.currency,
            status='Unpaid'
        )

        order_item = OrderItem.objects.create(
            order=order,
            item=item,
            quantity=1,
            price=item.price,
            currency=item.currency,
            item_name=item.name
        )
        if taxes:
            order_item.taxes.set(taxes)

        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(
            request, f"Произошла непредвиденная ошибка при создании платежа: {e}")
        return redirect('item', item_slug=item_slug)


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
    total_price_without_taxes = cart.get_total_price()
    tax_amount = cart.get_tax_amount()
    total_quantity = cart.get_total_quantity()

    currencies = set(cart_item.item.currency for cart_item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        "total_price": total_price_without_taxes,
        "tax_amount": tax_amount,
        "total_quantity": total_quantity,
        'title': 'Корзина',
        'has_multiple_currencies': len(currencies) > 1,
        'currencies': currencies,
        "default_image": settings.DEFAULT_ITEM_IMAGE,
    }

    return render(request, 'shop/cart.html', context)


@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
    return redirect('view_cart')


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


@login_required
def create_session_success(request):
    session_id = request.GET.get('session_id')

    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)

            order = Order.objects.get(
                stripe_session_id=session.id,
                user=request.user
            )

            if session.payment_status == 'paid':
                order.status = 'Paid'
                order.save()

                Cart.objects.get(user=request.user).items.all().delete()

            return render(request, 'shop/success.html', {'order': order})

        except Exception as e:
            return render(request, 'home', {'error': 'Ошибка платежной системы'})

    return render(request, 'shop/success.html')


@login_required
def create_session_cart(request):
    cart = get_object_or_404(Cart, user=request.user)

    if cart.is_empty():
        return redirect('view_cart')

    items = cart.items.select_related('item').all()

    currencies = set(item.item.currency for item in items)
    if len(currencies) > 1:
        return redirect('view_cart')

    unavailable_items = items.filter(item__is_available=False)
    if unavailable_items.exists():
        item_names = [item.item.name for item in unavailable_items]
        messages.error(
            request,
            f"Следующие товары больше не доступны: {', '.join(item_names)}"
        )
        return redirect('view_cart')

    total_spent = request.user.get_total_spent()
    current_rank = RankCategory.objects.filter(
        min_total__lte=total_spent
    ).order_by('-min_total').first()
    discount = current_rank.discount
    coupon = discount.stripe_coupon_id if discount.is_active else None

    currency = items[0].item.currency
    try:
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': cart_item.item.currency.code,
                        'product_data': {'name': cart_item.item.name},
                        'unit_amount': int(cart_item.item.price * 100),
                    },
                    'quantity': cart_item.quantity,
                    'tax_rates': [tax.stripe_tax_id for tax in cart_item.item.taxes.all()],
                }
                for cart_item in items
            ],
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('create_session_success')
            ) + '?session_id={CHECKOUT_SESSION_ID}',
            discounts=[
                {'coupon': f"{current_rank.discount.stripe_coupon_id}"}] if coupon else None
        )

        order = Order.objects.create(
            user=request.user,
            stripe_session_id=session.id,
            total_amount=cart.get_total_price(),
            currency=currency,
            status='Unpaid'
        )

        for cart_item in items:
            OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                quantity=cart_item.quantity,
                price=cart_item.item.price,
                currency=cart_item.item.currency,
                item_name=cart_item.item.name
            ).taxes.set(cart_item.item.taxes.all())

        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(
            request, f"Произошла непредвиденная ошибка при создании платежа: {e}")
        return redirect('view_cart')


@login_required
def payment_intent_success(request):
    """Страница успешной оплаты через PaymentIntent"""
    payment_intent_id = request.GET.get('payment_intent')

    if not payment_intent_id:
        messages.warning(request, "Не указан идентификатор платежа")
        return redirect('view_cart')

    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if payment_intent.status == 'succeeded':
            try:
                order = Order.objects.get(
                    stripe_payment_intent_id=payment_intent_id)
                order.status = 'Paid'
                order.save()

                Cart.objects.filter(user=request.user).delete()

            except Order.DoesNotExist:
                messages.warning(request, "Заказ не найден в системе")
            except Cart.DoesNotExist:
                pass

        return render(request, 'shop/payment_success.html', {
            'title': 'Оплата успешна',
            'payment_intent': payment_intent,
            'amount': payment_intent.amount / 100,
            'currency': payment_intent.currency.upper(),
        })

    except stripe.error.InvalidRequestError:
        messages.error(request, "Неверный идентификатор платежа")
        return redirect('view_cart')
    except Exception as e:
        messages.error(request, f"Ошибка при обработке платежа: {str(e)}")
        return redirect('view_cart')


@login_required
def payment_intent(request):
    """Payment Intent"""
    try:
        cart = get_object_or_404(Cart, user=request.user)

        if cart.is_empty():
            messages.info(request, "Корзина пуста")
            return redirect('view_cart')

        cart_items = cart.items.select_related('item', 'item__currency').all()

        currencies = set(item.item.currency for item in cart_items)
        if len(currencies) > 1:
            messages.error(request, "Товары в разных валютах")
            return redirect('view_cart')

        currency = cart_items[0].item.currency

        item_details = []
        base_price_total = 0
        tax_amount_total = 0

        for cart_item in cart_items:
            item = cart_item.item
            quantity = cart_item.quantity
            item_base_price = item.price * quantity
            base_price_total += item_base_price

            taxes = item.taxes.all()
            item_tax = 0
            if taxes.exists():
                for tax in taxes:
                    if not tax.inclusive:
                        item_tax += item_base_price * (tax.percentage / 100)
                tax_amount_total += item_tax

            item_details.append({
                'name': item.name,
                'quantity': quantity,
                'price': item.price,
                'total': item_base_price,
                'taxes': taxes,
                'tax_amount': item_tax,
                'image': item.image,
                'slug': item.slug,
            })

        total_amount = base_price_total + tax_amount_total

        total_spent = request.user.get_total_spent()
        current_rank = RankCategory.objects.filter(
            min_total__lte=total_spent
        ).order_by('-min_total').first()

        discount_amount = 0
        discount_percent = 0
        rank_name = None

        if current_rank and current_rank.discount and current_rank.discount.is_active:
            rank_name = current_rank.name
            if current_rank.discount.percent_off:
                discount_percent = current_rank.discount.percent_off
                discount_amount = total_amount * (discount_percent / 100)
                total_amount -= discount_amount
            elif current_rank.discount.amount_off:
                discount_amount = current_rank.discount.amount_off
                total_amount -= discount_amount

        payment_intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),
            currency=currency.code.lower(),
            automatic_payment_methods={"enabled": True},
            metadata={
                "user_id": str(request.user.id),
                "items_count": str(len(cart_items)),
                "base_price": str(base_price_total),
                "tax_amount": str(tax_amount_total),
                "discount": str(discount_amount),
                "rank": rank_name or "none",
            }
        )

        order = Order.objects.create(
            user=request.user,
            stripe_payment_intent_id=payment_intent.id,
            total_amount=total_amount,
            currency=currency,
            status='Unpaid'
        )

        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                item=cart_item.item,
                quantity=cart_item.quantity,
                price=cart_item.item.price,
                currency=cart_item.item.currency,
                item_name=cart_item.item.name
            )
            if cart_item.item.taxes.exists():
                order_item.taxes.set(cart_item.item.taxes.all())

        return render(request, 'shop/payment_intent.html', {
            'title': 'Оплата заказа',
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'order_id': order.id,
            'items': item_details,
            'items_count': len(cart_items),
            'base_price_total': base_price_total,
            'tax_amount_total': tax_amount_total,
            'discount_amount': discount_amount,
            'discount_percent': discount_percent,
            'total_amount': total_amount,
            'currency': currency.symbol,
            'rank_name': rank_name,
            'default_image': settings.DEFAULT_ITEM_IMAGE,
        })

    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect('view_cart')
