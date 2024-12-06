from django.db import models

class CurrencyRate(models.Model):
    currency_code = models.CharField(max_length=10)
    currency_name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now=True)
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.currency_code} - {self.exchange_rate}"
