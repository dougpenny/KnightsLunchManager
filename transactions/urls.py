from logging import basicConfig
from django.urls import path

from transactions.views import DeleteTransactionView, ExportChecksView
from transactions.views import OrderProcessView, TransactionsDateArchiveView, TransactionDetailView
from transactions.views import TransactionListView, TransactionsTodayArchiveView
from transactions.views import batch_deposit, deposit_checklist, new_single_deposit, new_single_order


urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('<int:year>/<int:month>/<int:day>/',
         TransactionsDateArchiveView.as_view(month_format='%m'), name='transaction-date-list'),
    path('today/', TransactionsTodayArchiveView.as_view(),
         name='transaction-today-list'),

    path('delete/', DeleteTransactionView.as_view(), name='admin-delete'),

    path('deposits/', TransactionListView.as_view(filter='deposits'), name='transaction-deposits'),
    path('deposit/<int:pk>/', TransactionDetailView.as_view(filter='deposits'), name='transaction-deposit-detail'),
    path('deposits/checklist/', deposit_checklist, name='deposit-checklist'),
    path('deposits/export-checks/', ExportChecksView.as_view(), name='misc-receipts-report'),
    path('deposits/<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(filter='deposits', month_format='%m'), name='transaction-date-deposits'),
    path('deposits/checklist/<int:year>/<int:month>/<int:day>/', deposit_checklist, name='deposit-checklist-day'),
    path('deposits/export-checks/<int:year>/<int:month>/<int:day>/', ExportChecksView.as_view(), name='misc-receipts-report-day'),
    path('deposit/new/', new_single_deposit, name='transaction-deposit-create'),
    path('deposits/today/', TransactionsTodayArchiveView.as_view(filter='deposits'), name='transaction-today-deposits'),
    path('deposits/batch/', batch_deposit, name='transaction-deposits-batch'),

    path('orders/', TransactionListView.as_view(filter='orders'),
         name='transaction-orders'),
    path('order/<int:pk>/', TransactionDetailView.as_view(filter='orders'),
         name='transaction-detail-order'),
    path('orders/<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(
        filter='orders', month_format='%m'), name='transaction-date-orders'),
    path('orders/today/', TransactionsTodayArchiveView.as_view(filter='orders'),
         name='transaction-today-orders'),
    path('order/new/', new_single_order, name='transaction-order-create'),
    path('orders/process/<int:year>/<int:month>/<int:day>/',
         OrderProcessView.as_view(), name='transaction-date-process'),
    path('order/process/<int:pk>/', OrderProcessView.as_view(),
         name='transaction-single-process'),
]
