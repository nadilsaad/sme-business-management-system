from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivityLogViewSet,
    CategoryViewSet,
    CustomerViewSet,
    DashboardView,
    DebtViewSet,
    ExpenseViewSet,
    LoginView,
    MeView,
    PaymentViewSet,
    ProductViewSet,
    ReportView,
    RoleViewSet,
    SaleViewSet,
    StockMovementViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("roles", RoleViewSet, basename="role")
router.register("users", UserViewSet, basename="user")
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("inventory/movements", StockMovementViewSet, basename="stock-movement")
router.register("customers", CustomerViewSet, basename="customer")
router.register("sales", SaleViewSet, basename="sale")
router.register("expenses", ExpenseViewSet, basename="expense")
router.register("debts", DebtViewSet, basename="debt")
router.register("payments", PaymentViewSet, basename="payment")
router.register("activities", ActivityLogViewSet, basename="activity")

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("reports/", ReportView.as_view(), name="reports"),
    path("", include(router.urls)),
]
