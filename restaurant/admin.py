from django.contrib import admin

from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "is_available",
    )

    list_filter = (
        "category",
        "is_available",
    )

    search_fields = (
        "name",
        "description",
    )

    list_editable = (
        "price",
        "stock",
        "is_available",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "unit_price",
        "quantity",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "phone",
        "city",
        "total",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "city",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "email",
        "phone",
        "address",
    )

    list_editable = (
        "status",
    )

    readonly_fields = (
        "subtotal",
        "delivery_fee",
        "total",
        "created_at",
        "updated_at",
    )

    inlines = (
        OrderItemInline,
    )