from django.contrib import admin
from .models import Card, Order, Product, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0


class CardAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Card._meta.fields]
    inlines = [OrderInline]


class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.fields]
    inlines = [OrderProductInline]


class ProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Product._meta.fields]


class OrderProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderProduct._meta.fields]


admin.site.register(Card, CardAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
