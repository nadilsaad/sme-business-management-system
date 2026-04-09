from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from business.models import Category, Customer, Debt, Expense, Payment, Product, Role, Sale, SaleItem, StockMovement, User, log_activity


class Command(BaseCommand):
    help = "Seed demo data for SME Business Management System"

    @transaction.atomic
    def handle(self, *args, **options):
        roles = {
            "ADMIN": Role.objects.get_or_create(code="ADMIN", defaults={"name": "Admin", "description": "System administrator"})[0],
            "CASHIER": Role.objects.get_or_create(code="CASHIER", defaults={"name": "Cashier", "description": "Handles checkout and receipts"})[0],
            "STORE_KEEPER": Role.objects.get_or_create(code="STORE_KEEPER", defaults={"name": "Store Keeper", "description": "Manages inventory"})[0],
        }

        demo_users = [
            ("admin", "Admin User", roles["ADMIN"]),
            ("cashier", "Cashier User", roles["CASHIER"]),
            ("storekeeper", "Store Keeper", roles["STORE_KEEPER"]),
        ]
        for username, full_name, role in demo_users:
            user, created = User.objects.get_or_create(username=username, defaults={"full_name": full_name, "role": role, "email": f"{username}@demo.local"})
            user.role = role
            user.full_name = full_name
            user.set_password("demo1234")
            user.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created user {username}"))

        categories = {}
        for name in ["Salon", "Boutique", "Pharmacy", "Stationery", "General Shop"]:
            categories[name], _ = Category.objects.get_or_create(name=name)

        products_data = [
            ("Hair Food", "SAL-001", "Salon", 12000, 8000, 18),
            ("Body Lotion", "BOT-001", "Boutique", 15000, 9500, 10),
            ("Painkiller", "PHA-001", "Pharmacy", 5000, 2500, 24),
            ("Exercise Book", "STA-001", "Stationery", 2500, 1200, 6),
            ("Soft Drink", "GEN-001", "General Shop", 2000, 1200, 30),
        ]

        products = {}
        for name, sku, category_name, price, cost, stock in products_data:
            product, _ = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "name": name,
                    "category": categories[category_name],
                    "selling_price": Decimal(price),
                    "cost_price": Decimal(cost),
                    "stock_quantity": stock,
                    "low_stock_threshold": 5,
                },
            )
            products[sku] = product

        customers = {}
        for name, phone in [("Neema John", "0712345678"), ("Asha Ally", "0755001122"), ("Moses Peter", "0688002211")]:
            customers[name], _ = Customer.objects.get_or_create(name=name, defaults={"phone": phone})

        admin = User.objects.get(username="admin")
        cashier = User.objects.get(username="cashier")

        Expense.objects.get_or_create(title="Rent April", defaults={"category": "Rent", "amount": Decimal("350000"), "created_by": admin})
        Expense.objects.get_or_create(title="Electricity Tokens", defaults={"category": "Utilities", "amount": Decimal("85000"), "created_by": admin})
        Expense.objects.get_or_create(title="Internet Bundle", defaults={"category": "Utilities", "amount": Decimal("45000"), "created_by": admin})

        sale, _ = Sale.objects.get_or_create(
            receipt_number="RCPT-DEMO-001",
            defaults={
                "customer": customers["Neema John"],
                "cashier": cashier,
                "subtotal": Decimal("22000"),
                "discount": Decimal("2000"),
                "total_amount": Decimal("20000"),
                "amount_paid": Decimal("15000"),
                "balance_due": Decimal("5000"),
            },
        )
        if not sale.items.exists():
            SaleItem.objects.create(sale=sale, product=products["SAL-001"], quantity=1, unit_price=Decimal("12000"), line_total=Decimal("12000"))
            SaleItem.objects.create(sale=sale, product=products["GEN-001"], quantity=5, unit_price=Decimal("2000"), line_total=Decimal("10000"))
            StockMovement.objects.get_or_create(product=products["SAL-001"], movement_type=StockMovement.MOVEMENT_OUT, quantity=1, reference=sale.receipt_number, created_by=cashier)
            StockMovement.objects.get_or_create(product=products["GEN-001"], movement_type=StockMovement.MOVEMENT_OUT, quantity=5, reference=sale.receipt_number, created_by=cashier)
            products["SAL-001"].stock_quantity = max(products["SAL-001"].stock_quantity - 1, 0)
            products["GEN-001"].stock_quantity = max(products["GEN-001"].stock_quantity - 5, 0)
            products["SAL-001"].save(update_fields=["stock_quantity", "updated_at"])
            products["GEN-001"].save(update_fields=["stock_quantity", "updated_at"])

        debt, _ = Debt.objects.get_or_create(
            sale=sale,
            defaults={
                "customer": customers["Neema John"],
                "total_amount": Decimal("20000"),
                "paid_amount": Decimal("15000"),
                "remaining_balance": Decimal("5000"),
            },
        )
        Payment.objects.get_or_create(
            sale=sale,
            amount=Decimal("15000"),
            method=Payment.METHOD_MOBILE,
            defaults={"customer": customers["Neema John"], "debt": debt, "received_by": cashier, "reference": "MPESA-7788"},
        )

        log_activity("seed_data_loaded", "Demo data seeded for SME Business Management System", actor=admin)
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
