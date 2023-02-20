from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone


class Card(models.Model):
    """Модель карты"""
    NOT_ACTIVATED = 'Не активирована'
    ACTIVATED = 'Активирована'
    OVERDUE = 'Просрочена'

    STATUS = [
        (NOT_ACTIVATED, 'Не активирована'),
        (ACTIVATED, 'Активирована'),
        (OVERDUE, 'Просрочена'),
    ]

    serial = models.CharField(max_length=2, verbose_name='Серия карты')
    number = models.IntegerField(verbose_name='Номер карты')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время выпуска карты')
    start_activate_date = models.DateTimeField(verbose_name='Дата и время активации карты', blank=True, null=True)
    date_of_last_use = models.DateTimeField(auto_now=True, verbose_name='Дата и время последнего использования')
    finish_date = models.DateTimeField(verbose_name='Дата и время окончания активности карты')
    orders_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='Сумма покупок', default=0)
    card_status = models.CharField(max_length=16, choices=STATUS, default=NOT_ACTIVATED, verbose_name='Статус карты')
    discount = models.DecimalField(max_digits=3, decimal_places=1, verbose_name='Текущая скидка (%)', default=0)
    trash = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.serial} {self.number}'

    class Meta:
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'


class Order(models.Model):
    """Модель заказа"""
    card = models.ForeignKey('Card', on_delete=models.CASCADE, blank=True, null=True)
    date_of_purchase = models.DateTimeField(auto_now=True, verbose_name='Дата и время покупки')
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма заказа', default=0)
    discount = models.DecimalField(max_digits=3, decimal_places=1, verbose_name='Скидка (%)', default=0)
    total_amount_with_discount = models.DecimalField(max_digits=15, decimal_places=2,
                                                     verbose_name='Сумма заказа с учётом скидки', default=0)
    discount_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма скидки', default=0)

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Product(models.Model):
    """Модель продукта"""
    product_name = models.CharField(max_length=255, verbose_name='Наименование товара')
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена')
    price_with_discount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена со скидкой',
                                              blank=True, null=True)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class OrderProduct(models.Model):
    """Связь между заказом и продуктами в заказе"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество штук')
    price_per_item = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Цена', default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Итого', default=0)

    def __str__(self):
        return str(self.product)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def save(self, *args, **kwargs):
        """Расчет стоимостей по товару в заказе"""
        price_per_item_with_discount = self.product.price_with_discount
        if price_per_item_with_discount:
            self.price_per_item = price_per_item_with_discount
            self.total_amount = self.quantity * price_per_item_with_discount
        else:
            price_per_item = self.product.price
            self.price_per_item = price_per_item
            self.total_amount = self.quantity * price_per_item

        super(OrderProduct, self).save(*args, **kwargs)


def product_in_order_post_save(sender, instance, created, **kwargs):
    """Расчет стоимости всего заказа"""
    order = instance.order
    all_products_in_order = OrderProduct.objects.filter(order=order)

    order_total_amount = 0
    for product in all_products_in_order:
        order_total_amount += product.total_amount

    if instance.order.card.card_status == 'Активирована':

        discount = instance.order.card.discount
        instance.order.discount = discount

        with_discount = (order_total_amount * (100 - discount)) / 100
        instance.order.total_amount_with_discount = with_discount

        total_discount = order_total_amount - with_discount
        instance.order.discount_value = total_discount
    else:
        instance.order.total_amount_with_discount = order_total_amount

    instance.order.total_amount = order_total_amount
    instance.order.save(force_update=True)


def order_post_save(sender, instance, created, **kwargs):
    """Расчет общей стоимости заказов по карте"""
    card = instance.card
    all_orders = Order.objects.filter(card=card)

    card_total_amount = 0
    for order in all_orders:
        card_total_amount += order.total_amount_with_discount

    instance.card.orders_amount = card_total_amount
    instance.card.save(force_update=True)


post_save.connect(product_in_order_post_save, sender=OrderProduct)
post_save.connect(order_post_save, sender=Order)
