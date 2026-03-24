import os
import csv
import requests
from datetime import date, datetime
from django.core.management.base import BaseCommand
from currex_app.models import Currency, ExchangeRate

class Command(BaseCommand):
    help = 'Генерує CSV файл з курсами відстежуваних валют за вказану дату (або за сьогодні)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Дата у форматі YYYY-MM-DD. Якщо не вказано, береться сьогоднішня дата.'
        )

    def handle(self, *args, **options):
        date_str = options['date']
        if date_str:
            try:
                target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR("Помилка: Неправильний формат дати. Використовуйте YYYY-MM-DD"))
                return
        else:
            target_date = date.today()

        tracked_currencies = Currency.objects.filter(is_tracked=True)
        if not tracked_currencies.exists():
            self.stdout.write(self.style.WARNING("Немає жодної відстежуваної валюти. Поставте галочки в адмінці!"))
            return

        rates_in_db = ExchangeRate.objects.filter(date=target_date, currency__in=tracked_currencies)
        
        if rates_in_db.count() < tracked_currencies.count():
            self.stdout.write(self.style.WARNING(f"Не всі курси за {target_date} є в базі. Завантажую з НБУ..."))
            self.fetch_from_nbu(target_date, tracked_currencies)
            rates_in_db = ExchangeRate.objects.filter(date=target_date, currency__in=tracked_currencies)

        export_dir = 'results'
        os.makedirs(export_dir, exist_ok=True)
        filename = f"tracked_rates_{target_date.strftime('%Y-%m-%d')}.csv"
        file_path = os.path.join(export_dir, filename)
        
        with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';') # Використовуємо крапку з комою (стандарт для українського Excel)
            
            writer.writerow(['Дата', 'Код', 'Назва валюти', 'Курс (UAH)'])
            
            for rate_obj in rates_in_db:
                writer.writerow([
                    rate_obj.date.strftime('%d.%m.%Y'),
                    rate_obj.currency.code,
                    rate_obj.currency.name,
                    rate_obj.rate
                ])
                
        self.stdout.write(self.style.SUCCESS(f"✅ Успіх! Файл збережено як: {filename}"))

    def fetch_from_nbu(self, target_date, tracked_currencies):
        """Допоміжна функція для завантаження даних з НБУ за конкретну дату"""
        nbu_date_format = target_date.strftime('%Y%m%d')
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={nbu_date_format}&json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            tracked_dict = {c.code: c for c in tracked_currencies}
            
            for item in data:
                code = item['cc']
                if code in tracked_dict:
                    ExchangeRate.objects.update_or_create(
                        currency=tracked_dict[code],
                        date=target_date,
                        defaults={'rate': item['rate']}
                    )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Помилка при завантаженні з НБУ: {e}"))