from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True   )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    popularity = models.IntegerField(default=0) 

    def __str__(self):
        return self.name