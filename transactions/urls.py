from django.urls import path

from transactions.views import TransactionCreateView, TransactionDetailView, TransactionListView, TransactionDepositView


urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('deposit/', TransactionDepositView.as_view(), name='transaction-deposit'),
]