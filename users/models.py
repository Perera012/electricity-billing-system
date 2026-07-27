from django.db import models


class TariffRate(models.Model):
    slab_name = models.CharField(max_length=50)
    min_units = models.IntegerField()
    max_units = models.IntegerField()
    rate_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_charge = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.slab_name