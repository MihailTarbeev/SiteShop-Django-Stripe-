from django import forms
from .models import Item
from .utils import MIN_AMOUNTS


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["image", "name", "price", "currency", "description",
                  "is_available", "category", "slug", "taxes"]

    def clean(self):
        price = self.cleaned_data.get('price')
        currency = self.cleaned_data.get('currency')
        currency_code = currency.code
        if price * 100 < MIN_AMOUNTS[currency_code]:
            raise forms.ValidationError({
                'price': f'Минимальная стоимость для данной валюты: {MIN_AMOUNTS[currency_code] / 100}'
            })
        return self.cleaned_data


class AddToCartForm(forms.Form):
    """Форма добавления товара в корзину"""
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'quantity-input',
            'min': '1',
            'max': '99'
        })
    )
