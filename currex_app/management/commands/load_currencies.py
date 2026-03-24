from datetime import datetime

import requests
from django.core.management.base import BaseCommand
from currex_app.models import Currency, ExchangeRate

class Command(BaseCommand):
    help = 'Завантажує довідник усіх доступних валют з НБУ'

    def handle(self, *args, **kwargs):
        self.stdout.write('Завантаження даних з НБУ...')
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            added_count = 0
            for item in data:
                currency, created = Currency.objects.update_or_create(
                    code=item['cc'], 
                    defaults={
                        'name': item['txt'], 
                        'price_now': item['rate'], 
                        'is_tracked': False   
                    }
                )

                currency, created = ExchangeRate.objects.get_or_create(
                    currency=currency,
                    date=datetime.strptime(item['exchangedate'], "%d.%m.%Y").date(),
                    defaults={'rate': item['rate']}
                )

                if created:
                    added_count += 1

            self.stdout.write(self.style.SUCCESS(f'Успішно завершено! Додано {added_count} нових валют.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Помилка завантаження: {e}'))