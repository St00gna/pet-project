from celery import shared_task
from django.core.management import call_command
import logging

# Налаштовуємо логування, щоб бачити результат у терміналі Docker
logger = logging.getLogger(__name__)

@shared_task
def auto_export_currencies_csv():
    logger.info("Починаю автоматичне завантаження та генерацію CSV...")
    try:
        call_command('export_csv')
        logger.info("✅ Автоматичний експорт успішно завершено!")
        return "Success"
    except Exception as e:
        logger.error(f"❌ Помилка під час автоматичного експорту: {e}")
        return f"Error: {e}"