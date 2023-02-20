import datetime
import pytz
from celery import shared_task

from .models import Card


@shared_task
def check_card_period(pk):
    """Таска для проверки срока действия карты"""
    while True:
        try:
            card = Card.objects.get(pk=pk)
            if card.finish_date < datetime.datetime.now(tz=pytz.timezone('Europe/Moscow')):
                card.card_status = 'Просрочена'
                card.save(force_update=True)
                return
        except:
            return


@shared_task
def check_active_card_period(pk):
    """Таска для проверки срока активности карты"""
    while True:
        try:
            card = Card.objects.get(pk=pk)
            if (card.start_activate_date < (datetime.datetime.now(
                    tz=pytz.timezone('Europe/Moscow')))) and (card.finish_date > (datetime.datetime.now(
                    tz=pytz.timezone('Europe/Moscow')))):
                card.card_status = 'Активирована'
                card.save(force_update=True)
                return
        except:
            return
