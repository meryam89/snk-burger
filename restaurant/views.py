from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product


def home(request):
    return render(
        request,
        "restaurant/home.html",
    )


def menu(request):
    categories = Category.objects.filter(
        is_active=True
    ).prefetch_related("products")

    products = Product.objects.filter(
        is_available=True,
        stock__gt=0,
    ).select_related("category")

    return render(
        request,
        "restaurant/menu.html",
        {
            "categories": categories,
            "products": products,
        },
    )


def get_cart_details(request):
    cart = request.session.get("cart", {})

    products = Product.objects.filter(
        id__in=cart.keys(),
        is_available=True,
    )

    items = []
    total = Decimal("0.00")

    for product in products:
        product_key = str(product.id)
        quantity = int(cart.get(product_key, 0))
        subtotal = product.price * quantity

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

        total += subtotal

    return items, total


def cart_detail(request):
    items, total = get_cart_details(request)

    return render(
        request,
        "restaurant/cart.html",
        {
            "items": items,
            "total": total,
        },
    )


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    cart = request.session.get("cart", {})
    product_key = str(product.id)
    quantity = int(cart.get(product_key, 0))

    if quantity < product.stock:
        cart[product_key] = quantity + 1

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(
            request,
            f"{product.name} a été ajouté au panier.",
        )
    else:
        messages.error(
            request,
            "Le stock disponible est insuffisant.",
        )

    return redirect("restaurant:cart")


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_key = str(product_id)

    if product_key in cart:
        del cart[product_key]

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(
            request,
            "Le produit a été supprimé du panier.",
        )

    return redirect("restaurant:cart")
@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    cart = request.session.get("cart", {})
    product_key = str(product.id)

    if product_key not in cart:
        return redirect("restaurant:cart")

    quantity = int(cart[product_key])
    action = request.POST.get("action")

    if action == "increase":
        if quantity < product.stock:
            cart[product_key] = quantity + 1
        else:
            messages.error(
                request,
                "Stock maximum atteint.",
            )

    elif action == "decrease":
        if quantity > 1:
            cart[product_key] = quantity - 1
        else:
            del cart[product_key]

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("restaurant:cart")

def checkout(request):
    items, subtotal = get_cart_details(request)

    if not items:
        messages.error(
            request,
            "Votre panier est vide.",
        )
        return redirect("restaurant:home")

    delivery_fee = Decimal("2.50")
    total = subtotal + delivery_fee

    form = CheckoutForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.customer = request.user

            order.subtotal = subtotal
            order.delivery_fee = delivery_fee
            order.total = total
            order.save()

            for item in items:
                product = item["product"]
                quantity = item["quantity"]

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    unit_price=product.price,
                    quantity=quantity,
                )

                product.stock -= quantity
                product.save(update_fields=["stock"])

        request.session["cart"] = {}
        request.session.modified = True

        return render(
            request,
            "restaurant/order_success.html",
            {
                "order": order,
            },
        )

    return render(
        request,
        "restaurant/checkout.html",
        {
            "form": form,
            "items": items,
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "total": total,
        },
    )

@login_required
def order_history(request):
    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related(
        "items",
        "items__product",
    )

    return render(
        request,
        "restaurant/order_history.html",
        {
            "orders": orders,
        },
    )


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        customer=request.user,
    )

    delivery_steps = [
        ("pending", "Commande reçue"),
        ("confirmed", "Commande confirmée"),
        ("preparing", "En préparation"),
        ("delivering", "En livraison"),
        ("delivered", "Commande livrée"),
    ]

    status_values = [
        status for status, label in delivery_steps
    ]

    try:
        current_position = status_values.index(order.status)
    except ValueError:
        current_position = -1

    steps = []

    for position, (status, label) in enumerate(delivery_steps):
        steps.append(
            {
                "status": status,
                "label": label,
                "completed": position <= current_position,
                "current": position == current_position,
            }
        )

    return render(
        request,
        "restaurant/order_detail.html",
        {
            "order": order,
            "steps": steps,
        },
    )