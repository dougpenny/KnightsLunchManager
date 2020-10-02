from django.urls import path

from transactions.views import BatchDepositView, CreateDepositView
from transactions.views import CreateOrderView, ExportChecksView
from transactions.views import OrderProcessView, TransactionsDateArchiveView, TransactionDetailView
from transactions.views import TransactionListView, TransactionsTodayArchiveView


urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(month_format='%m'), name='transaction-date-list'),
    path('today/', TransactionsTodayArchiveView.as_view(), name='transaction-today-list'),

    path('deposits/', TransactionListView.as_view(filter='deposits'), name='transaction-deposits'),
    path('deposit/<int:pk>/', TransactionDetailView.as_view(filter='deposits'), name='transaction-deposit-detail'),
    path('deposits/export-checks/', ExportChecksView.as_view(), name='transaction-export-checks'),
    path('deposits/<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(filter='deposits', month_format='%m'), name='transaction-date-deposits'),
    path('deposits/export-checks/<int:year>/<int:month>/<int:day>/', ExportChecksView.as_view(), name='transaction-date-export-checks'),
    path('deposit/new/', CreateDepositView.as_view(), name='transaction-deposit-create'),
    path('deposits/today/', TransactionsTodayArchiveView.as_view(filter='deposits'), name='transaction-today-deposits'),
    path('deposits/batch', BatchDepositView.as_view(), name='transaction-deposits-batch'),

    path('orders/', TransactionListView.as_view(filter='orders'), name='transaction-orders'),
    path('order/<int:pk>/', TransactionDetailView.as_view(filter='orders'), name='transaction-detail-order'),
    path('orders/<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(filter='orders', month_format='%m'), name='transaction-date-orders'),
    path('orders/today/', TransactionsTodayArchiveView.as_view(filter='orders'), name='transaction-today-orders'),
    path('order/new/', CreateOrderView.as_view(), name='transaction-order-create'),
    path('orders/process/<int:year>/<int:month>/<int:day>/', OrderProcessView.as_view(), name='transaction-date-process'),
    path('order/process/<int:pk>/', OrderProcessView.as_view(), name='transaction-single-process'),
]