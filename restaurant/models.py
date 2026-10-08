from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom",
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Catégorie active",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )


class Meta:
    verbose_name = "Catégorie"
    verbose_name_plural = "Catégories"
    ordering = ["name"]


def __str__(self):
    return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Catégorie",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nom",
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
    )

    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Prix",
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        verbose_name="Image",
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock",
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="Disponible",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ["category", "name"]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.is_available and self.stock > 0


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        CONFIRMED = "confirmed", "Confirmée"
        PREPARING = "preparing", "En préparation"
        DELIVERING = "delivering", "En livraison"
        DELIVERED = "delivered", "Livrée"
        CANCELLED = "cancelled", "Annulée"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Client",
    )

    customer_name = models.CharField(
        max_length=120,
        verbose_name="Nom du client",
    )

    email = models.EmailField(
        verbose_name="Adresse e-mail",
    )

    phone = models.CharField(
        max_length=30,
        verbose_name="Téléphone",
    )

    address = models.CharField(
        max_length=255,
        verbose_name="Adresse de livraison",
    )

    city = models.CharField(
        max_length=100,
        verbose_name="Ville",
    )

    postal_code = models.CharField(
        max_length=20,
        verbose_name="Code postal",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Instructions de livraison",
    )

    subtotal = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Sous-total",
    )

    delivery_fee = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=2.50,
        verbose_name="Frais de livraison",
    )

    total = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        verbose_name="Total",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de commande",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        return f"Commande #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Commande",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Produit",
    )

    product_name = models.CharField(
        max_length=150,
        verbose_name="Nom du produit",
    )

    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Prix unitaire",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantité",
    )

    class Meta:
        verbose_name = "Article commandé"
        verbose_name_plural = "Articles commandés"

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity