from django.contrib import admin
from .models import TariffRate, MeterReading, Bill, Payment


# -----------------------------
# Tariff Rate Admin
# -----------------------------
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


# -----------------------------
# Meter Reading Admin
# -----------------------------
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
        'month',
    )

    readonly_fields = (
        'user',
        'month',
        'previous_reading',
        'current_reading',
        'units_used',
        'meter_image',
        'reading_date',
    )

    # Allow Add
    def has_add_permission(self, request):
        return True

    # Prevent editing existing records
    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

    # Prevent delete
    def has_delete_permission(self, request, obj=None):
        return False


# -----------------------------
# Bill Admin
# -----------------------------
@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'meter_reading',
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

    readonly_fields = (
        'user',
        'meter_reading',
        'total_amount',
        'bill_status',
        'created_at',
    )

    # Allow Add
    def has_add_permission(self, request):
        return True

    # Prevent editing
    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

    # Prevent delete
    def has_delete_permission(self, request, obj=None):
        return False


# -----------------------------
# Payment Admin
# -----------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'bill',
        'payment_method',
        'transaction_reference',
        'payment_status',
        'payment_date'
    )

    list_filter = (
        'payment_status',
    )

    search_fields = (
        'user__username',
        'transaction_reference',
    )

    readonly_fields = (
        'user',
        'bill',
        'payment_method',
        'transaction_reference',
        'payment_status',
        'payment_date',
    )

    # Allow Add
    def has_add_permission(self, request):
        return True

    # Prevent editing existing records
    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

    # Prevent delete
    def has_delete_permission(self, request, obj=None):
        return False