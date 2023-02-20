# Sellwin

## Базовые технологии проекта

- Python 3.11
- Django 4.1.6
- Django Rest Framework 3.14.0
- SQLite
- Celery 5.2.7
- Docker Desktop

#### Создание миграций, применять только при разработке:

```bash
python manage.py makemigrations
```

#### Применение миграций:

```bash
python manage.py migrate
```

#### Создание суперпользователя

```bash
python manage.py createsuperuser
```

#### Внешние порты

- 5432:5432 - БД
- 8000:8000 - API
- 16379:6379 - REDIS


#### Описание задания

Тестовое задание Python/Django (flask) – простая система управления лояльностями.
Необходимо разработать веб-приложение для управления базой данных бонусных карт.

Справочники:

- % скидки: Наименование, % (может быть дробным)

Основной список полей/таблиц:

- Карты: серия карты, номер карты дата и время выпуска карты, дата и время окончания активности карты, дата и время последнего использования, сумма покупок, статус карты (не активирована / активирована / просрочена), % текущая скидка, заказы;
- Заказы(покупки): Номер, дата и время, сумма, % скидки (для конкретного заказа), скидка (расчет)
- Товары:  заказ, наименование товара, цена, цена со скидкой

Функции приложения:

- список карт с полями: серия, номер, дата выпуска, дата окончания активности, статус
- поиск по этим же полям
- просмотр профиля карты с историей покупок по ней
- активация/деактивация карты
- удаление карты (сперва в корзину с возможностью восстановления)
- генератор карт, с указанием серии и количества генерируемых карт, а срока активности «с-по».
- после истечения срока активности карты, у карты проставляется статус "просрочена".

Функции интеграции:
- необходимо реализовать REST API для интеграции с сервисом;
- получение информации по номеру карты (информация по карте, информация по заказам и товарам карты с возможностью фильтрации по датам);
- записи информации по заказам и товарам для определенной карты.
