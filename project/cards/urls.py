from django.urls import path, include
from rest_framework import routers
from .views import index, add_card, card_detail, card_delete, card_edit, trash_bin, card_delete_in_trash, recover, \
    add_some_cards, CardViewSet, OrderViewSet, ProductViewSet, OrderProductViewSet

router = routers.DefaultRouter()

router.register(r'cards', CardViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'products', ProductViewSet)
router.register(r'ordersproducts', OrderProductViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('trash-bin/', trash_bin, name='trash_bin'),
    path('add-card/', add_card, name='add_card'),
    path('add-some-cards/', add_some_cards, name='add_some_cards'),
    path('<int:pk>/', card_detail, name='card_detail'),
    path('<int:pk>/delete-in-trash/', card_delete_in_trash, name='card_delete_in_trash'),
    path('<int:pk>/recover/', recover, name='recover'),
    path('<int:pk>/delete/', card_delete, name='card_delete'),
    path('<int:pk>/edit/', card_edit, name='card_edit'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
