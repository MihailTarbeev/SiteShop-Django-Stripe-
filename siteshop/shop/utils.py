

def get_currency_choices():
    """Получить выборку валют из модели Currency"""
    from .models import Currency
    currencies = Currency.objects.filter(is_active=True).order_by('code')
    return [(currency.code.lower(), currency.symbol) for currency in currencies]


def get_min_amounts():
    """Получить минимальные суммы для Stripe"""
    from .models import Currency
    currencies = Currency.objects.filter(is_active=True)
    return {
        currency.code.lower(): int(float(currency.min_amount) * 100)
        for currency in currencies
    }


def get_stripe_min_amount(currency_code):
    """Получить минимальную сумму для конкретной валюты в минимальных единицах"""
    from .models import Currency
    currency = Currency.objects.get(code__iexact=currency_code)
    return int(float(currency.min_amount) * 100)


CURRENCY_CHOICES = get_currency_choices()
MIN_AMOUNTS = get_min_amounts()
