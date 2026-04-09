from decimal import Decimal

from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from .models import (
    ActivityLog,
    Category,
    Customer,
    Debt,
    Expense,
    Payment,
    Product,
    Role,
    Sale,
    SaleItem,
    StockMovement,
    User,
    adjust_stock,
    log_activity,
)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "code", "description"]


class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), source="role", write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "role_id",
            "is_active",
        ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password.")
        attrs["user"] = user
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "updated_at"]


class CustomerSerializer(serializers.ModelSerializer):
    current_debt_balance = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "address",
            "notes",
            "current_debt_balance",
            "created_at",
            "updated_at",
        ]

    def get_current_debt_balance(self, obj):
        return obj.debts.filter(status=Debt.STATUS_OPEN).aggregate(total=Sum("remaining_balance")).get("total") or Decimal("0")


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "sku",
            "description",
            "unit",
            "selling_price",
            "cost_price",
            "stock_quantity",
            "low_stock_threshold",
            "is_active",
            "is_low_stock",
            "created_at",
            "updated_at",
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "product_name",
            "movement_type",
            "quantity",
            "reference",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
        ]


class StockAdjustmentSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")
    movement_type = serializers.ChoiceField(choices=StockMovement.MOVEMENT_TYPES)
    quantity = serializers.IntegerField(min_value=1)
    reference = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        actor = self.context["request"].user
        product = validated_data["product"]
        adjust_stock(
            product=product,
            quantity=validated_data["quantity"],
            movement_type=validated_data["movement_type"],
            actor=actor,
            reference=validated_data.get("reference", ""),
            notes=validated_data.get("notes", ""),
        )
        log_activity(
            action="stock_adjusted",
            description=f"{validated_data['movement_type']} {validated_data['quantity']} units of {product.name}",
            actor=actor,
            related_instance=product,
        )
        return product.stock_movements.first()


class SaleItemWriteSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")
    quantity = serializers.IntegerField(min_value=1)


class PaymentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    sale_receipt_number = serializers.CharField(source="sale.receipt_number", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "sale",
            "sale_receipt_number",
            "customer",
            "customer_name",
            "debt",
            "amount",
            "method",
            "reference",
            "received_by",
            "notes",
            "created_at",
        ]


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    sku = serializers.CharField(source="product.sku", read_only=True)

    class Meta:
        model = SaleItem
        fields = ["id", "product", "product_name", "sku", "quantity", "unit_price", "line_total"]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    cashier_name = serializers.CharField(source="cashier.full_name", read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "receipt_number",
            "customer",
            "customer_name",
            "cashier",
            "cashier_name",
            "subtotal",
            "discount",
            "total_amount",
            "amount_paid",
            "balance_due",
            "status",
            "notes",
            "items",
            "payments",
            "created_at",
        ]


class SaleCreateSerializer(serializers.Serializer):
    customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), source="customer", required=False, allow_null=True)
    discount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=Decimal("0"))
    notes = serializers.CharField(required=False, allow_blank=True)
    amount_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    payment_reference = serializers.CharField(required=False, allow_blank=True)
    items = SaleItemWriteSerializer(many=True)

    def validate(self, attrs):
        if not attrs["items"]:
            raise serializers.ValidationError({"items": "At least one item is required."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        actor = self.context["request"].user
        items = validated_data.pop("items")
        customer = validated_data.get("customer")
        discount = validated_data.get("discount", Decimal("0"))
        amount_paid = validated_data["amount_paid"]
        payment_method = validated_data["payment_method"]
        payment_reference = validated_data.get("payment_reference", "")

        subtotal = Decimal("0")
        receipt_number = f"RCPT-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        sale = Sale.objects.create(
            receipt_number=receipt_number,
            customer=customer,
            cashier=actor,
            discount=discount,
            amount_paid=amount_paid,
            notes=validated_data.get("notes", ""),
        )

        for item in items:
            product = item["product"]
            quantity = item["quantity"]
            if product.stock_quantity < quantity:
                raise serializers.ValidationError({"items": f"Insufficient stock for {product.name}."})
            line_total = product.selling_price * quantity
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=product.selling_price,
                line_total=line_total,
            )
            adjust_stock(
                product=product,
                quantity=quantity,
                movement_type=StockMovement.MOVEMENT_OUT,
                actor=actor,
                reference=receipt_number,
                notes="Sale completed",
            )
            subtotal += line_total

        total_amount = subtotal - discount
        balance_due = total_amount - amount_paid
        if balance_due < 0:
            raise serializers.ValidationError({"amount_paid": "Amount paid cannot exceed total amount."})

        sale.subtotal = subtotal
        sale.total_amount = total_amount
        sale.balance_due = balance_due
        sale.save(update_fields=["subtotal", "total_amount", "balance_due", "updated_at"])

        Payment.objects.create(
            sale=sale,
            customer=customer,
            amount=amount_paid,
            method=payment_method,
            reference=payment_reference,
            received_by=actor,
        )

        if balance_due > 0:
            if not customer:
                raise serializers.ValidationError({"customer_id": "Customer is required for partial payments."})
            Debt.objects.update_or_create(
                sale=sale,
                defaults={
                    "customer": customer,
                    "total_amount": total_amount,
                    "paid_amount": amount_paid,
                    "remaining_balance": balance_due,
                    "status": Debt.STATUS_OPEN,
                },
            )

        log_activity(
            action="sale_completed",
            description=f"Sale {receipt_number} completed for TZS {total_amount}",
            actor=actor,
            related_instance=sale,
        )
        return sale


class ExpenseSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "title",
            "category",
            "amount",
            "expense_date",
            "vendor",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by"]


class DebtSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    sale_receipt_number = serializers.CharField(source="sale.receipt_number", read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Debt
        fields = [
            "id",
            "customer",
            "customer_name",
            "sale",
            "sale_receipt_number",
            "total_amount",
            "paid_amount",
            "remaining_balance",
            "status",
            "due_date",
            "notes",
            "payments",
            "created_at",
            "updated_at",
        ]


class DebtPaymentCreateSerializer(serializers.Serializer):
    debt_id = serializers.PrimaryKeyRelatedField(queryset=Debt.objects.all(), source="debt")
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)
    reference = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    @transaction.atomic
    def create(self, validated_data):
        actor = self.context["request"].user
        debt = validated_data["debt"]
        amount = validated_data["amount"]
        if amount <= 0 or amount > debt.remaining_balance:
            raise serializers.ValidationError({"amount": "Amount must be positive and not exceed remaining balance."})

        payment = Payment.objects.create(
            sale=debt.sale,
            customer=debt.customer,
            debt=debt,
            amount=amount,
            method=validated_data["method"],
            reference=validated_data.get("reference", ""),
            received_by=actor,
            notes=validated_data.get("notes", ""),
        )
        debt.refresh_balance(save=True)
        debt.sale.amount_paid = debt.sale.payments.aggregate(total=Sum("amount")).get("total") or Decimal("0")
        debt.sale.balance_due = debt.remaining_balance
        debt.sale.save(update_fields=["amount_paid", "balance_due", "updated_at"])
        log_activity(
            action="debt_payment_received",
            description=f"Debt payment of TZS {amount} received from {debt.customer.name}",
            actor=actor,
            related_instance=payment,
        )
        return payment


class ActivityLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.full_name", read_only=True)

    class Meta:
        model = ActivityLog
        fields = ["id", "action", "description", "related_model", "related_id", "actor_name", "created_at"]
