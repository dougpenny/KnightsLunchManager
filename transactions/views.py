
from django.http import HttpResponse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, FormView, DayArchiveView, TodayArchiveView

from .models import Transaction
from .forms import TransactionForm, TransactionDepositForm


class TransactionMixin:
    filter = None
    allow_empty = True
    date_field = "submitted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        context['today'] = timezone.now
        return context

    def get_queryset(self):
        if self.filter == 'deposits':
            return Transaction.objects.filter(transaction_type=Transaction.CREDIT)
        elif self.filter == 'orders':
            return Transaction.objects.filter(transaction_type=Transaction.DEBIT)
        else:
            return Transaction.objects.all()


class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_create.html'
    queryset = Transaction.objects.all()


class TransactionListView(TransactionMixin, ListView):
    template_name = 'transactions/transactions_list.html'


class TransactionsDateArchiveView(TransactionMixin, DayArchiveView):
    template_name = 'transactions/transactions_list.html'


class TransactionsTodayArchiveView(TransactionMixin, TodayArchiveView):
    template_name = 'transactions/transactions_list.html'


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


class TransactionProcessView(View):
    def get(self, request, *args, **kwargs):
        if self.kwargs['year']:
            print('Year: {}'.format(self.kwargs['year']))
        if self.kwargs['month']:
            print('Year: {}'.format(self.kwargs['month']))
        if self.kwargs['day']:
            print('Year: {}'.format(self.kwargs['day']))
        if self.kwargs['pk']:
            print('Year: {}'.format(self.kwargs['pk']))
        return HttpResponse('Hello, World!')