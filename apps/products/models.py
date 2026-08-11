from django.db import models
from django.db.models import Q

# Create your models here.
class Product(models.Model):
    sku = models.CharField(max_length = 50, unique=True)
    name = models.CharField(max_length = 200)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
    )

    stock_quantity = models.PositiveIntegerField(default = 0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition = Q(price__gt=0),
                name="product_price_gt_zero",
            ),
        ]

    def __str__(self):
        return f"{self.sku} {self.name}"
