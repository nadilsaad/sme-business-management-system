from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}".strip() or self.username
        super().save(*args, **kwargs)

    @property
    def role_code(self):
        return self.role.code if self.role else None


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Customer(TimeStampedModel):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=30, default="pcs")
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))], default=0)
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_product_name_per_category")
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold


class StockMovement(TimeStampedModel):
    MOVEMENT_IN = "IN"
    MOVEMENT_OUT = "OUT"
    MOVEMENT_ADJUSTMENT = "ADJUSTMENT"
    MOVEMENT_TYPES = [
        (MOVEMENT_IN, "Stock In"),
        (MOVEMENT_OUT, "Stock Out"),
        (MOVEMENT_ADJUSTMENT, "Adjustment"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="stock_movements")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} {self.movement_type} {self.quantity}"


class Sale(TimeStampedModel):
    STATUS_COMPLETED = "COMPLETED"
    STATUS_VOIDED = "VOIDED"
    STATUS_CHOICES = [
        (STATUS_COMPLETED, "Completed"),
        (STATUS_VOIDED, "Voided"),
    ]

    receipt_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_COMPLETED)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.receipt_number


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Expense(TimeStampedModel):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField(default=timezone.localdate)
    vendor = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses")

    class Meta:
        ordering = ["-expense_date", "-created_at"]

    def __str__(self):
        return self.title


class Debt(TimeStampedModel):
    STATUS_OPEN = "OPEN"
    STATUS_PAID = "PAID"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_PAID, "Paid"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="debts")
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name="debt")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["status", "-created_at"]

    def __str__(self):
        return f"{self.customer.name} - {self.remaining_balance}"

    def refresh_balance(self, save=True):
        paid = self.payments.aggregate(total=Sum("amount")).get("total") or Decimal("0")
        self.paid_amount = paid
        self.remaining_balance = self.total_amount - self.paid_amount
        self.status = self.STATUS_PAID if self.remaining_balance <= 0 else self.STATUS_OPEN
        if save:
            self.save(update_fields=["paid_amount", "remaining_balance", "status", "updated_at"])


class Payment(TimeStampedModel):
    METHOD_CASH = "CASH"
    METHOD_MOBILE = "MOBILE_MONEY"
    METHOD_BANK = "BANK_TRANSFER"
    METHOD_CHOICES = [
        (METHOD_CASH, "Cash"),
        (METHOD_MOBILE, "Mobile Money"),
        (METHOD_BANK, "Bank Transfer"),
    ]

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="payments")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    debt = models.ForeignKey(Debt, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments_received")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.method} - {self.amount}"


class ActivityLog(TimeStampedModel):
    action = models.CharField(max_length=120)
    description = models.TextField()
    related_model = models.CharField(max_length=80, blank=True)
    related_id = models.PositiveIntegerField(null=True, blank=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.action


def log_activity(action, description, actor=None, related_instance=None):
    ActivityLog.objects.create(
        action=action,
        description=description,
        actor=actor,
        related_model=related_instance.__class__.__name__ if related_instance else "",
        related_id=related_instance.id if related_instance else None,
    )


@transaction.atomic
def adjust_stock(product, quantity, movement_type, actor=None, reference="", notes=""):
    if movement_type == StockMovement.MOVEMENT_OUT and product.stock_quantity < quantity:
        raise ValueError(f"Insufficient stock for {product.name}")
    if movement_type == StockMovement.MOVEMENT_OUT:
        product.stock_quantity -= quantity
    elif movement_type == StockMovement.MOVEMENT_IN:
        product.stock_quantity += quantity
    else:
        product.stock_quantity += quantity
    product.save(update_fields=["stock_quantity", "updated_at"])
    StockMovement.objects.create(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        reference=reference,
        notes=notes,
        created_by=actor,
    )
