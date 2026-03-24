import os
from datetime import date
from unittest.mock import patch
from django.test import TestCase
from django.core.management import call_command
from django.db import IntegrityError

from currex_app.models import Currency, ExchangeRate

class CurrencyModelTest(TestCase):
    def setUp(self):
        self.currency = Currency.objects.create(
            code='USD', 
            name='Долар США', 
            is_tracked=True
        )

    def test_currency_creation(self):
        self.assertEqual(self.currency.code, 'USD')
        self.assertTrue(self.currency.is_tracked)
        self.assertEqual(str(self.currency), 'USD - Долар США')

    def test_exchange_rate_unique_constraint(self):
        ExchangeRate.objects.create(currency=self.currency, rate=39.5, date=date(2026, 3, 24))

        with self.assertRaises(IntegrityError):
            ExchangeRate.objects.create(currency=self.currency, rate=40.0, date=date(2026, 3, 24))


class CommandsTest(TestCase):
    @patch('currex_app.management.commands.load_currencies.requests.get')
    def test_load_currencies_command(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"r030": 840, "txt": "Долар США", "rate": 39.5, "cc": "USD", "exchangedate": "24.03.2026"},
            {"r030": 978, "txt": "Євро", "rate": 42.1, "cc": "EUR", "exchangedate": "24.03.2026"}
        ]

        call_command('load_currencies')

        self.assertEqual(Currency.objects.count(), 2)
        self.assertTrue(Currency.objects.filter(code='USD').exists())
        self.assertFalse(Currency.objects.get(code='USD').is_tracked) # За замовчуванням має бути False

    @patch('currex_app.management.commands.create_csv.requests.get')
    def test_export_csv_command(self, mock_get):
        
        Currency.objects.create(code='EUR', name='Євро', is_tracked=True)

        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"r030": 978, "txt": "Євро", "rate": 42.5, "cc": "EUR", "exchangedate": "24.03.2026"}
        ]

        call_command('create_csv', date='2026-03-24')

        self.assertEqual(ExchangeRate.objects.count(), 1)
        self.assertEqual(ExchangeRate.objects.first().rate, 42.5)

        expected_file_path = os.path.join('results', 'tracked_rates_2026-03-24.csv')
        self.assertTrue(os.path.exists(expected_file_path))

        if os.path.exists(expected_file_path):
            os.remove(expected_file_path)