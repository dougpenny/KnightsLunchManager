
from django.views.generic import CreateView, ListView, DetailView, FormView

from .models import Transaction
from .forms import TransactionForm, TransactionDepositForm


class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_create.html'
    queryset = Transaction.objects.all()

class TransactionListView(ListView):
    template_name = 'transactions/transactions_list.html'
    queryset = Transaction.objects.all()

class TransactionDetailView(DetailView):
    template_name = 'transactions/transaction_detail.html'
    queryset = Transaction.objects.all()


class TransactionDepositView(FormView):
    form_class = TransactionDepositForm
    template_name = 'transactions/transaction_single_deposit.html'
    success_url = '/admin/transactions/'

    def form_valid(self, form):
        print('User ID: {}'.format(form.cleaned_data['transactee']))
        print('Check #: {}'.format(form.cleaned_data['check_num']))
        print('Amount: {}'.format(form.cleaned_data['amount']))
        return super().form_valid(form)
