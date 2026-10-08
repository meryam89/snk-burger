from django.urls import path

from . import views


app_name = "restaurant"

urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "menu/",
        views.menu,
        name="menu",
    ),
    path(
        "panier/",
        views.cart_detail,
        name="cart",
    ),
    path(
        "panier/ajouter/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),
    path(
        "panier/supprimer/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path(
        "panier/modifier/<int:product_id>/",
        views.update_cart,
        name="update_cart",
    ),
    path(
        "commander/",
        views.checkout,
        name="checkout",
    ),
    path(
        "mes-commandes/",
        views.order_history,
        name="order_history",
    ),
    path(
        "mes-commandes/<int:order_id>/",
        views.order_detail,
        name="order_detail",
    ),
]