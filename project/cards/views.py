from django.shortcuts import render, redirect
from django.contrib import messages
from django_filters.rest_framework import DjangoFilterBackend
from .models import Card, Order, Product, OrderProduct
from .forms import AddCardForm, AddSomeCards
from random import randrange
from .tasks import check_card_period, check_active_card_period
from rest_framework import viewsets
from .serializers import CardSerializer, OrderSerializer, ProductSerializer, OrderProductSerializer


class CardViewSet(viewsets.ModelViewSet):
    """Отображение списка карт с возможностью фильтрации по полям"""
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['serial', 'number', 'card_status']

    def get_queryset(self):
        return Card.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    """Отображение списка заказов с возможностью фильтрации по полям"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['card']

    def get_queryset(self):
        return Order.objects.all()


class ProductViewSet(viewsets.ModelViewSet):
    """Отображение списка продуктов с возможностью фильтрации по полям"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['product_name']

    def get_queryset(self):
        return Product.objects.all()


class OrderProductViewSet(viewsets.ModelViewSet):
    """Отображение списка продуктов в заказе с возможностью фильтрации по полям"""
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['order', 'product']

    def get_queryset(self):
        return OrderProduct.objects.all()


def index(request):
    """Отображение списка карт с возможностью поиска по полям"""
    search_by = request.GET.get('search_by')
    query = request.GET.get('query')

    if query:
        if search_by == "serial":
            cards = Card.objects.filter(trash=False).filter(serial__icontains=query)
        elif search_by == "number":
            cards = Card.objects.filter(trash=False).filter(number__icontains=query)
        elif search_by == "create_date":
            cards = Card.objects.filter(trash=False).filter(create_date__icontains=query)
        elif search_by == "finish_date":
            cards = Card.objects.filter(trash=False).filter(finish_date__icontains=query)
        elif search_by == "card_status":
            cards = Card.objects.filter(trash=False).filter(card_status__icontains=query)
    else:
        cards = Card.objects.filter(trash=False)

    return render(request, 'cards/index.html', {'cards': cards})


def card_detail(request, pk):
    """Отображение деталей по карте со списком совершенных покупок"""
    card = Card.objects.get(pk=pk)
    orders = Order.objects.filter(card=card)

    context = {
        'card': card,
        'orders': orders,
    }

    return render(request, 'cards/card_detail.html', context)


def card_delete_in_trash(request, pk):
    """Удаление карты в корзину"""
    card = Card.objects.get(pk=pk)
    card.trash = True
    card.save()

    messages.success(request, 'The card was deleted in trash bin.')

    return redirect('index')


def recover(request, pk):
    """Восстановление карты из корзины"""
    card = Card.objects.get(pk=pk)
    card.trash = False
    card.save()

    check_active_card_period.delay(card.pk)
    check_card_period.delay(card.pk)

    messages.success(request, 'The card was recovered.')

    return redirect('trash_bin')


def card_delete(request, pk):
    """Удаление карты из корзины навсегда"""
    card = Card.objects.get(pk=pk)
    card.delete()

    messages.success(request, 'The card was deleted.')

    return redirect('trash_bin')


def card_edit(request, pk):
    """"Редактирование данных по карте (активность карты, срок действия, скидка)"""
    card = Card.objects.get(pk=pk)

    if request.method == 'POST':
        form = AddCardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()

            check_active_card_period.delay(card.pk)
            check_card_period.delay(card.pk)

            messages.success(request, 'The changes was saved.')

            return redirect('index')
    else:
        form = AddCardForm(instance=card)

    return render(request, 'cards/edit_card.html', {'form': form})


def add_card(request):
    """Добавление новой карты"""
    if request.method == 'POST':
        form = AddCardForm(request.POST)

        if form.is_valid():
            card = form.save()
            card.save()

            check_active_card_period.delay(card.pk)
            check_card_period.delay(card.pk)

            messages.success(request, 'The card was created.')

            return redirect('index')
    else:
        form = AddCardForm()

    return render(request, 'cards/add_card.html', {'form': form})


def add_some_cards(request):
    """Генерация нескольких карт"""
    if request.method == 'POST':
        form = AddSomeCards(request.POST)

        if form.is_valid():
            data = {
                'serial': form.cleaned_data['serial'],
                'count': form.cleaned_data['count'],
                'activated': form.cleaned_data['activated'],
                'deactivated': form.cleaned_data['deactivated'],
            }
            count = int(data['count'])
            for i in range(count):
                card_number = randrange(10000000, 100000000)
                check = Card.objects.filter(serial=data['serial']).filter(number=card_number)
                if not check:
                    card = Card(serial=data['serial'],
                                number=card_number,
                                start_activate_date=data['activated'],
                                finish_date=data['deactivated'])
                    card.save()

                    check_active_card_period.delay(card.pk)
                    check_card_period.delay(card.pk)
                else:
                    count += 1

            messages.success(request, f'The {data["count"]} cards was created.')

            return redirect('index')
    else:
        form = AddSomeCards()

    return render(request, 'cards/add_some_cards.html', {'form': form})


def trash_bin(request):
    """Отображение карт в корзине"""
    cards = Card.objects.filter(trash=True)
    return render(request, 'cards/trash_bin.html', {'cards': cards})
