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
        if price * 100 < MIN_AMOUNTS[currency]:
            raise forms.ValidationError({
                'price': f'Минимальная стоимость для данной валюты: {MIN_AMOUNTS[currency] / 100}'
            })
        return self.cleaned_data
