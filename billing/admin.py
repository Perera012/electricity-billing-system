from django.contrib import admin
from .models import TariffRate, MeterReading, Bill, Payment


@admin.register(TariffRate)
class TariffRateAdmin(admin.ModelAdmin):
    list_display = (
        'slab_name',
        'min_units',
        'max_units',
        'rate_per_unit',
        'fixed_charge'
    )

    search_fields = ('slab_name',)


@admin.register(MeterReading)
class MeterReadingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'month',
        'previous_reading',
        'current_reading',
        'units_used',
        'reading_date'
    )

    search_fields = (
        'user__username',
        'month'
    )


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'total_amount',
        'bill_status',
        'created_at'
    )

    list_filter = (
        'bill_status',
    )

    search_fields = (
        'user__username',
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'bill',
        'payment_method',
        'payment_status',
        'payment_date'
    )

    list_filter = (
        'payment_status',
    )

    search_fields = (
        'user__username',
        'transaction_reference'
    )