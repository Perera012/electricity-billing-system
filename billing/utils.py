from decimal import Decimal
from .models import TariffRate


def calculate_bill(units):
    units = int(units)

    total = Decimal("0.00")

    tariffs = TariffRate.objects.order_by("min_units")

    for tariff in tariffs:

        if units >= tariff.min_units:

            upper_limit = min(units, tariff.max_units)

            slab_units = upper_limit - tariff.min_units + 1

            if slab_units > 0:
                total += Decimal(slab_units) * tariff.rate_per_unit

    applicable_tariff = TariffRate.objects.filter(
        min_units__lte=units,
        max_units__gte=units
    ).first()

    if applicable_tariff:
        total += applicable_tariff.fixed_charge

    return total