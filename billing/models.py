from django.db import models
from django.contrib.auth.models import User


class TariffRate(models.Model):
    slab_name = models.CharField(max_length=50)
    min_units = models.IntegerField()
    max_units = models.IntegerField()
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.slab_name


class MeterReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    previous_reading = models.IntegerField()
    current_reading = models.IntegerField()
    units_used = models.IntegerField()
    meter_image = models.ImageField(upload_to='meter_images/', blank=True, null=True)
    reading_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.month}"


class Bill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meter_reading = models.ForeignKey(MeterReading, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bill_status = models.CharField(max_length=20, default='Unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill - {self.user.username}"


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    transaction_reference = models.CharField(
    max_length=100,
    unique=True
)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.payment_status}"