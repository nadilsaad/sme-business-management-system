from datetime import datetime

from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ActivityLog, Category, Customer, Debt, Expense, Payment, Product, Role, Sale, StockMovement, User
from .permissions import AdminOnly, AdminOrCashier, AdminOrStoreKeeper, AuthenticatedReadOnly
from .serializers import (
    ActivityLogSerializer,
    CategorySerializer,
    CustomerSerializer,
    DebtPaymentCreateSerializer,
    DebtSerializer,
    ExpenseSerializer,
    LoginSerializer,
    PaymentSerializer,
    ProductSerializer,
    RoleSerializer,
    SaleCreateSerializer,
    SaleSerializer,
    StockAdjustmentSerializer,
    StockMovementSerializer,
    UserSerializer,
)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("role").all()
    serializer_class = UserSerializer
    permission_classes = [AdminOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "full_name", "email"]
    ordering_fields = ["username", "full_name", "created_at"]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrStoreKeeper]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [AdminOrStoreKeeper]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "sku", "category__name"]
    ordering_fields = ["name", "stock_quantity", "selling_price", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        low_stock = self.request.query_params.get("low_stock")
        if category:
            queryset = queryset.filter(category_id=category)
        if low_stock == "true":
            queryset = queryset.filter(stock_quantity__lte=F("low_stock_threshold"))
        return queryset


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AuthenticatedReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "phone", "email"]
    ordering_fields = ["name", "created_at"]


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockMovement.objects.select_related("product", "created_by").all()
    serializer_class = StockMovementSerializer
    permission_classes = [AdminOrStoreKeeper]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product__name", "reference", "notes"]
    ordering_fields = ["created_at", "quantity"]

    @action(detail=False, methods=["post"], permission_classes=[AdminOrStoreKeeper])
    def adjust(self, request):
        serializer = StockAdjustmentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        movement = serializer.save()
        return Response(StockMovementSerializer(movement).data, status=status.HTTP_201_CREATED)


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related("customer", "cashier").prefetch_related("items__product", "payments").all()
    serializer_class = SaleSerializer
    permission_classes = [AdminOrCashier]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["receipt_number", "customer__name", "cashier__full_name"]
    ordering_fields = ["created_at", "total_amount"]

    def get_serializer_class(self):
        if self.action == "create":
            return SaleCreateSerializer
        return SaleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()
        return Response(SaleSerializer(sale).data, status=status.HTTP_201_CREATED)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.select_related("created_by").all()
    serializer_class = ExpenseSerializer
    permission_classes = [AdminOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "category", "vendor"]
    ordering_fields = ["expense_date", "amount", "created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DebtViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Debt.objects.select_related("customer", "sale").prefetch_related("payments").all()
    serializer_class = DebtSerializer
    permission_classes = [AuthenticatedReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["customer__name", "sale__receipt_number"]
    ordering_fields = ["remaining_balance", "created_at"]

    @action(detail=False, methods=["post"], permission_classes=[AdminOrCashier])
    def collect_payment(self, request):
        serializer = DebtPaymentCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("sale", "customer", "received_by", "debt").all()
    serializer_class = PaymentSerializer
    permission_classes = [AuthenticatedReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["sale__receipt_number", "customer__name", "reference"]
    ordering_fields = ["created_at", "amount"]


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.select_related("actor").all()[:50]
    serializer_class = ActivityLogSerializer
    permission_classes = [AuthenticatedReadOnly]


class DashboardView(APIView):
    def get(self, request):
        today = timezone.localdate()
        start_of_month = today.replace(day=1)

        sales_today = Sale.objects.filter(created_at__date=today, status=Sale.STATUS_COMPLETED).aggregate(total=Sum("total_amount")).get("total") or 0
        sales_month = Sale.objects.filter(created_at__date__gte=start_of_month, status=Sale.STATUS_COMPLETED).aggregate(total=Sum("total_amount")).get("total") or 0
        expenses_month = Expense.objects.filter(expense_date__gte=start_of_month).aggregate(total=Sum("amount")).get("total") or 0
        open_debts = Debt.objects.filter(status=Debt.STATUS_OPEN).aggregate(total=Sum("remaining_balance")).get("total") or 0
        low_stock_count = Product.objects.filter(stock_quantity__lte=F("low_stock_threshold")).count()

        sales_trend = list(
            Sale.objects.filter(created_at__date__gte=start_of_month, status=Sale.STATUS_COMPLETED)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(total=Sum("total_amount"), transactions=Count("id"))
            .order_by("day")
        )

        category_mix = list(
            Sale.objects.filter(status=Sale.STATUS_COMPLETED)
            .values("items__product__category__name")
            .annotate(total=Sum("items__line_total"))
            .order_by("-total")[:5]
        )

        recent_activities = ActivityLogSerializer(ActivityLog.objects.select_related("actor").all()[:8], many=True).data
        low_stock_products = ProductSerializer(
            Product.objects.filter(stock_quantity__lte=F("low_stock_threshold")).order_by("stock_quantity")[:8],
            many=True,
        ).data

        return Response(
            {
                "kpis": {
                    "sales_today": sales_today,
                    "sales_month": sales_month,
                    "expenses_month": expenses_month,
                    "open_debts": open_debts,
                    "low_stock_count": low_stock_count,
                },
                "sales_trend": sales_trend,
                "category_mix": category_mix,
                "recent_activities": recent_activities,
                "low_stock_products": low_stock_products,
            }
        )


class ReportView(APIView):
    def get(self, request):
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        start_date = datetime.fromisoformat(start).date() if start else timezone.localdate().replace(day=1)
        end_date = datetime.fromisoformat(end).date() if end else timezone.localdate()

        sales = Sale.objects.filter(created_at__date__range=[start_date, end_date], status=Sale.STATUS_COMPLETED)
        expenses = Expense.objects.filter(expense_date__range=[start_date, end_date])
        payments = Payment.objects.filter(created_at__date__range=[start_date, end_date])

        top_products = (
            sales.values("items__product__name")
            .annotate(quantity=Sum("items__quantity"), revenue=Sum("items__line_total"))
            .order_by("-revenue")[:10]
        )

        return Response(
            {
                "range": {"start": start_date, "end": end_date},
                "summary": {
                    "sales_total": sales.aggregate(total=Sum("total_amount")).get("total") or 0,
                    "sales_count": sales.count(),
                    "expense_total": expenses.aggregate(total=Sum("amount")).get("total") or 0,
                    "payments_total": payments.aggregate(total=Sum("amount")).get("total") or 0,
                    "outstanding_debt": Debt.objects.filter(status=Debt.STATUS_OPEN).aggregate(total=Sum("remaining_balance")).get("total") or 0,
                },
                "top_products": list(top_products),
                "sales_by_day": list(
                    sales.annotate(day=TruncDate("created_at"))
                    .values("day")
                    .annotate(total=Sum("total_amount"))
                    .order_by("day")
                ),
                "expense_breakdown": list(
                    expenses.values("category")
                    .annotate(total=Sum("amount"))
                    .order_by("-total")
                ),
            }
        )
