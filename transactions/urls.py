from django.urls import path

from transactions.views import TransactionCreateView, TransactionsDateArchiveView, TransactionDetailView, TransactionListView, TransactionDepositView, TransactionsTodayArchiveView, TransactionProcessView


urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(month_format='%m'), name='transaction-date-list'),
    path('today/', TransactionsTodayArchiveView.as_view(), name='transaction-today-list'),

    path('deposits/', TransactionListView.as_view(filter='deposits'), name='transaction-deposits'),
    path('deposits/<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(filter='deposits', month_format='%m'), name='transaction-date-deposits'),
    path('deposits/new/', TransactionDepositView.as_view(), name='transaction-deposit-create'),
    path('deposits/today/', TransactionsTodayArchiveView.as_view(filter='deposits'), name='transaction-today-deposits'),

    path('orders/', TransactionListView.as_view(filter='orders'), name='transaction-orders'),
    path('orders/<int:year>/<int:month>/<int:day>/', TransactionsDateArchiveView.as_view(filter='orders', month_format='%m'), name='transaction-date-orders'),
    path('orders/today/', TransactionsTodayArchiveView.as_view(filter='orders'), name='transaction-today-orders'),
    path('orders/new/', TransactionDepositView.as_view(), name='transaction-order-create'),
    path('orders/process/<int:year>/<int:month>/<int:day>/', TransactionProcessView.as_view(), name='transaction-date-process'),
    path('orders/process/<int:pk>/', TransactionProcessView.as_view(), name='transaction-single-process'),

    path('create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
]