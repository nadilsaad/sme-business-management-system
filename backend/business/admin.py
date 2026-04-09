from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ActivityLog, Category, Customer, Debt, Expense, Payment, Product, Role, Sale, SaleItem, StockMovement, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    search_fields = ("name", "code")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Business Profile", {"fields": ("full_name", "phone", "role")}),
    )
    list_display = ("username", "full_name", "email", "role", "is_active")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "selling_price", "stock_quantity", "low_stock_threshold", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "created_at")
    search_fields = ("name", "phone", "email")


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "customer", "cashier", "total_amount", "amount_paid", "balance_due", "created_at")
    search_fields = ("receipt_number", "customer__name")
    inlines = [SaleItemInline]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "amount", "expense_date", "created_by")
    list_filter = ("category",)


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ("customer", "sale", "total_amount", "paid_amount", "remaining_balance", "status")
    list_filter = ("status",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("sale", "customer", "amount", "method", "received_by", "created_at")
    list_filter = ("method",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "movement_type", "quantity", "reference", "created_by", "created_at")
    list_filter = ("movement_type",)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "related_model", "created_at")
    search_fields = ("action", "description")
