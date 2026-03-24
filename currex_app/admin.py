from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.management import call_command

from .models import Currency, ExchangeRate

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price_now', 'is_tracked')
    list_filter = ('is_tracked',)
    search_fields = ('code', 'name')
    list_editable = ('is_tracked',)
    
    change_list_template = "admin/currency_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('load-from-nbu/', self.admin_site.admin_view(self.load_from_nbu), name='currency-load-nbu')
        ]
        return custom_urls + urls

    def load_from_nbu(self, request):
        try:
            call_command('load_currencies')
            self.message_user(request, "✅ Валюти успішно оновлено з бази НБУ!", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"❌ Помилка завантаження: {e}", level=messages.ERROR)
        
        return HttpResponseRedirect("../")

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'rate', 'date')
    list_filter = ('date', 'currency')
    search_fields = ('currency__code', 'currency__name')
    date_hierarchy = 'date'

    change_list_template = "admin/currency_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('load-from-nbu/', self.admin_site.admin_view(self.load_from_nbu), name='currency-load-nbu')
        ]
        return custom_urls + urls

    def load_from_nbu(self, request):
        try:
            call_command('load_currencies')
            self.message_user(request, "✅ Валюти успішно оновлено з бази НБУ!", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"❌ Помилка завантаження: {e}", level=messages.ERROR)
        
        return HttpResponseRedirect("../")