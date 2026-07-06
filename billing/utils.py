from decimal import Decimal


def calculate_bill(units):

    units = int(units)

    total = Decimal("0.00")
    fixed_charge = Decimal("0.00")

    if units <= 30:

        total += Decimal(units) * Decimal("5.00")
        fixed_charge = Decimal("80.00")

    elif units <= 60:

        total += Decimal(30) * Decimal("5.00")
        total += Decimal(units - 30) * Decimal("9.00")

        fixed_charge = Decimal("210.00")

    elif units <= 90:

        total += Decimal(30) * Decimal("5.00")
        total += Decimal(30) * Decimal("9.00")
        total += Decimal(units - 60) * Decimal("14.00")

        fixed_charge = Decimal("0.00")

    elif units <= 120:

        total += Decimal(30) * Decimal("5.00")
        total += Decimal(30) * Decimal("9.00")
        total += Decimal(30) * Decimal("14.00")
        total += Decimal(units - 90) * Decimal("20.00")

        fixed_charge = Decimal("400.00")

    elif units <= 180:

        total += Decimal(30) * Decimal("5.00")
        total += Decimal(30) * Decimal("9.00")
        total += Decimal(30) * Decimal("14.00")
        total += Decimal(30) * Decimal("20.00")
        total += Decimal(units - 120) * Decimal("28.00")

        fixed_charge = Decimal("1000.00")

    else:

        total += Decimal(30) * Decimal("5.00")
        total += Decimal(30) * Decimal("9.00")
        total += Decimal(30) * Decimal("14.00")
        total += Decimal(30) * Decimal("20.00")
        total += Decimal(60) * Decimal("28.00")
        total += Decimal(units - 180) * Decimal("44.00")

        fixed_charge = Decimal("1500.00")

    final_bill = total + fixed_charge

    return final_bill