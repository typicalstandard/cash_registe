from django.db import models

class Item(models.Model):
    title = models.CharField("Наименование", max_length=255)
    price = models.DecimalField("Стоимость", max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title
