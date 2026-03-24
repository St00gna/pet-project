from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    price_now = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    is_tracked = models.BooleanField(default=False)

    class Meta:
        db_table = 'currency'

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    date = models.DateField()

    class Meta:
        db_table = 'exchange_rate'
        constraints = [
            models.UniqueConstraint(
                fields=['currency', 'date'], 
                name='unique_currency_date'
            )
        ]

    def __str__(self):
        return f"{self.currency.code} - {self.rate} on {self.date}"