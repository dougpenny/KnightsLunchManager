import logging

from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, FormView, DayArchiveView, TodayArchiveView
from django.contrib import messages

from datetime import date

from profiles.models import Profile
from .models import Transaction
from .forms import TransactionForm, TransactionDepositForm


logger = logging.getLogger(__file__)


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


class TransactionDetailView(TransactionMixin, DetailView):
    template_name = 'transactions/transaction_detail.html'


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
    def process_transaction(self, order: Transaction):
        try:
            transactee = order.transactee
            order.beginning_balance = transactee.current_balance
            order.ending_balance = transactee.current_balance - order.amount
            order.completed = timezone.now()
            order.save()
            transactee.current_balance = order.ending_balance
            transactee.save()
        except:
            raise Exception

    def process_transactions_for_day(self, day: date) -> (bool, str):
        try:
            orders = Transaction.objects.filter(
                transaction_type=Transaction.DEBIT,
                submitted__date=day,
                completed__date=None,
            )
            if orders:
                for order in orders:
                    self.process_transaction(order)
                return True, 'Successfully processed {} transactions for {}.'.format(orders.count(), day.strftime('%b %-d, %Y'))
            else:
                raise Exception
        except:
            logger.info('When processing transactions, no transactions found for: {}'.format(day))
            return False, 'No transactions found on {} for processing.'.format(day.strftime('%b %-d, %Y'))

    def process_single_transaction(self, id: int) -> (bool, str):
        try:
            print('Transaction lookup: {}'.format(id))
            order = Transaction.objects.get(id=id)
            if not order.completed:
                self.process_transaction(order)
                return True, 'Successfully processed transaction #{}.'.format(id)
            else:
                raise Exception
        except:
            logger.info('When processing a transaction, no transaction found for id: {}'.format(id))
            return False, 'Transaction #{} was either not found or does not need to be processed.'.format(id)

    def get(self, request, *args, **kwargs):
        success = False
        message = None
        if ('year' in self.kwargs) and ('month' in self.kwargs) and ('day' in self.kwargs):
            day = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
            success, message = self.process_transactions_for_day(day)
        elif 'pk' in self.kwargs:
            success, message = self.process_single_transaction(self.kwargs['pk'])
        if success and message:
            messages.success(request, message)
        elif message:
            messages.warning(request, message)
        original_url = request.path_info
        elements = original_url.split('/')
        elements.remove('process')
        redirect_url = '/'.join(elements)
        return redirect(redirect_url)