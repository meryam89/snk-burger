
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product


class OrderSecurityTests(TestCase):

    def test_anonymous_user_cannot_access_order_history(self):
        response = self.client.get(
            reverse("restaurant:order_history")
        )

        self.assertEqual(response.status_code, 302)

    def test_user_cannot_access_another_users_order(self):
        User = get_user_model()

        # Création de deux clients
        client_a = User.objects.create_user(
            username="client_a",
            password="TestPassword123!",
        )

        client_b = User.objects.create_user(
            username="client_b",
            password="TestPassword123!",
        )

        # Une commande appartient au client A
        order = Order.objects.create(
            customer=client_a,
            customer_name="Client A",
            email="clienta@example.com",
            phone="0600000000",
            address="10 rue des Burgers",
            city="Paris",
            postal_code="75001",
            subtotal=Decimal("12.00"),
            delivery_fee=Decimal("2.50"),
            total=Decimal("14.50"),
        )

        # Le client B se connecte
        self.client.force_login(client_b)

        # Il essaie de consulter la commande du client A
        response = self.client.get(
            reverse(
                "restaurant:order_detail",
                args=[order.id],
            )
        )

        # L'accès doit être refusé
        self.assertEqual(response.status_code, 404)

    def test_user_can_access_own_order(self):
        User = get_user_model()

        # Création d'un client
        customer = User.objects.create_user(
            username="client_proprietaire",
            password="TestPassword123!",
        )

        # Création de sa commande
        order = Order.objects.create(
            customer=customer,
            customer_name="Client Propriétaire",
            email="client@example.com",
            phone="0600000000",
            address="15 rue des Burgers",
            city="Paris",
            postal_code="75001",
            subtotal=Decimal("12.00"),
            delivery_fee=Decimal("2.50"),
            total=Decimal("14.50"),
        )

        # Connexion du propriétaire
        self.client.force_login(customer)

        # Accès à sa propre commande
        response = self.client.get(
            reverse(
                "restaurant:order_detail",
                args=[order.id],
            )
        )

        # La page doit être accessible
        self.assertEqual(response.status_code, 200)

        # La bonne commande doit être affichée
        self.assertEqual(
            response.context["order"],
            order,
        )

    def test_order_history_only_shows_customer_orders(self):
        User = get_user_model()

        client_a = User.objects.create_user(
            username="historique_a",
            password="TestPassword123!",
        )

        client_b = User.objects.create_user(
            username="historique_b",
            password="TestPassword123!",
        )

        order_a = Order.objects.create(
            customer=client_a,
            customer_name="Client A",
            email="a@example.com",
            phone="0600000001",
            address="10 rue A",
            city="Paris",
            postal_code="75001",
            subtotal=Decimal("10.00"),
            delivery_fee=Decimal("2.50"),
            total=Decimal("12.50"),
        )

        order_b = Order.objects.create(
            customer=client_b,
            customer_name="Client B",
            email="b@example.com",
            phone="0600000002",
            address="20 rue B",
            city="Lyon",
            postal_code="69001",
            subtotal=Decimal("15.00"),
            delivery_fee=Decimal("2.50"),
            total=Decimal("17.50"),
        )

        self.client.force_login(client_a)

        response = self.client.get(
            reverse("restaurant:order_history")
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(order_a, response.context["orders"])
        self.assertNotIn(order_b, response.context["orders"])


    def test_add_product_to_cart(self):
        # Création d'une catégorie
        category = Category.objects.create(
            name="Burgers",
            slug="burgers",
        )

        # Création d'un produit
        product = Product.objects.create(
            category=category,
            name="Burger Test",
            slug="burger-test",
            price=Decimal("8.50"),
            stock=10,
            is_available=True,
        )

        # Ajout du produit au panier
        response = self.client.post(
            reverse(
                "restaurant:add_to_cart",
                args=[product.id],
            )
        )

        # Vérification de la redirection vers le panier
        self.assertRedirects(
            response,
            reverse("restaurant:cart"),
        )

        # Vérification du contenu du panier
        cart = self.client.session["cart"]

        self.assertEqual(
            cart[str(product.id)],
            1,
        )

    def test_increase_cart_quantity(self):
        # Création d'une catégorie
        category = Category.objects.create(
            name="Burgers",
            slug="burgers",
        )

        # Création d'un produit
        product = Product.objects.create(
            category=category,
            name="Burger Test",
            slug="burger-test",
            price=Decimal("8.50"),
            stock=10,
            is_available=True,
        )

        # Ajout d'un premier burger
        self.client.post(
            reverse(
                "restaurant:add_to_cart",
                args=[product.id],
            )
        )

        # Augmentation de la quantité
        response = self.client.post(
            reverse(
                "restaurant:update_cart",
                args=[product.id],
            ),
            {"action": "increase"},
        )

        # Vérification de la redirection
        self.assertRedirects(
            response,
            reverse("restaurant:cart"),
        )

        # Le panier doit contenir 2 burgers
        cart = self.client.session["cart"]

        self.assertEqual(
            cart[str(product.id)],
            2,
        )

    def test_decrease_cart_quantity(self):
        # Création d'une catégorie
        category = Category.objects.create(
            name="Burgers",
            slug="burgers",
        )

        # Création d'un produit
        product = Product.objects.create(
            category=category,
            name="Burger Test",
            slug="burger-test",
            price=Decimal("8.50"),
            stock=10,
            is_available=True,
        )

        # Ajout de deux burgers
        self.client.post(
            reverse(
                "restaurant:add_to_cart",
                args=[product.id],
            )
        )

        self.client.post(
            reverse(
                "restaurant:add_to_cart",
                args=[product.id],
            )
        )

        # Diminution de la quantité
        response = self.client.post(
            reverse(
                "restaurant:update_cart",
                args=[product.id],
            ),
            {"action": "decrease"},
        )

        # Vérification de la redirection
        self.assertRedirects(
            response,
            reverse("restaurant:cart"),
        )

        # Le panier doit contenir 1 burger
        cart = self.client.session["cart"]

        self.assertEqual(
            cart[str(product.id)],
            1,
        )

    def test_remove_product_from_cart(self):
        # Création d'une catégorie
        category = Category.objects.create(
            name="Burgers",
            slug="burgers",
        )

        # Création d'un produit
        product = Product.objects.create(
            category=category,
            name="Burger Test",
            slug="burger-test",
            price=Decimal("8.50"),
            stock=10,
            is_available=True,
        )

        # Ajout du produit au panier
        self.client.post(
            reverse(
                "restaurant:add_to_cart",
                args=[product.id],
            )
        )

        # Vérification : le produit est présent
        cart = self.client.session["cart"]

        self.assertIn(
            str(product.id),
            cart,
        )

        # Suppression du produit
        response = self.client.post(
            reverse(
                "restaurant:remove_from_cart",
                args=[product.id],
            )
        )

        # Vérification de la redirection
        self.assertRedirects(
            response,
            reverse("restaurant:cart"),
        )

        # Vérification : le produit a disparu
        cart = self.client.session["cart"]

        self.assertNotIn(
            str(product.id),
            cart,
        )

    def test_checkout_with_empty_cart_redirects_home(self):
        # Le panier est vide au début du test
        response = self.client.get(
            reverse("restaurant:checkout")
        )

        # Le client doit être redirigé vers l'accueil
        self.assertRedirects(
            response,
            reverse("restaurant:home"),
        )

        # Aucune commande ne doit être créée
        self.assertEqual(
            Order.objects.count(),
            0,
        )

    def test_cart_total_is_calculated_correctly(self):
        # Création d'une catégorie
        category = Category.objects.create(
            name="Burgers",
            slug="burgers",
        )

        # Création d'un burger à 8,50 €
        product = Product.objects.create(
            category=category,
            name="Burger Test",
            slug="burger-test",
            price=Decimal("8.50"),
            stock=10,
            is_available=True,
        )

        # Ajout de deux burgers au panier
        for _ in range(2):
            self.client.post(
                reverse(
                    "restaurant:add_to_cart",
                    args=[product.id],
                )
            )

        # Affichage du panier
        response = self.client.get(
            reverse("restaurant:cart")
        )

        # Vérification du montant total
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.context["total"],
            Decimal("17.00"),
        )

    def test_checkout_creates_order_and_updates_stock(self):
        # Création d'une catégorie
        category = Category.objects.create(
            name="Burgers",
            slug="burgers",
        )

        # Création d'un burger avec 10 unités en stock
        product = Product.objects.create(
            category=category,
            name="Burger Test",
            slug="burger-test",
            price=Decimal("8.50"),
            stock=10,
            is_available=True,
        )

        # Ajout de deux burgers au panier
        for _ in range(2):
            self.client.post(
                reverse(
                    "restaurant:add_to_cart",
                    args=[product.id],
                )
            )

        # Validation de la commande
        response = self.client.post(
            reverse("restaurant:checkout"),
            {
                "customer_name": "Client Test",
                "email": "client@example.com",
                "phone": "0600000000",
                "address": "10 rue des Burgers",
                "city": "Paris",
                "postal_code": "75001",
                "notes": "Sonner à la porte",
            },
        )

        # La page de confirmation doit s'afficher
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "restaurant/order_success.html",
        )

        # Une commande doit être enregistrée
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        # Vérification des montants
        self.assertEqual(
            order.subtotal,
            Decimal("17.00"),
        )

        self.assertEqual(
            order.delivery_fee,
            Decimal("2.50"),
        )

        self.assertEqual(
            order.total,
            Decimal("19.50"),
        )

        # La commande doit contenir deux burgers
        self.assertEqual(order.items.count(), 1)

        item = order.items.first()

        self.assertEqual(item.quantity, 2)

        # Le stock doit passer de 10 à 8
        product.refresh_from_db()

        self.assertEqual(product.stock, 8)

        # Le panier doit être vidé
        self.assertEqual(
            self.client.session["cart"],
            {},
        )

