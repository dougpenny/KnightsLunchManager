import io
import logging
import xlsxwriter

from django.http import FileResponse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, FormView, DayArchiveView, TodayArchiveView
from django.contrib import messages
from django.contrib.auth.models import User

from datetime import date

from menu.models import MenuItem
from profiles.models import Profile

from .models import Transaction, MenuLineItem
from .forms import TransactionForm, TransactionDepositForm, TransactionOrderForm, MenuLineItemFormSet, DepositFormSet


logger = logging.getLogger(__file__)


class DepositMixin:
    def create_deposit(self, deposit: dict) -> None:
        profile = Profile.objects.get(user__id=deposit['transactee'])
        new_balance = profile.current_balance + deposit['amount']
        description = ''
        if deposit['check_num'].lower() == 'lc':
            description = 'Previous lunch card balance'
        elif deposit['check_num'] == '':
            description = 'Cash'
        else:
            description = 'Check #' + deposit['check_num']
        transaction = Transaction(
            amount=deposit['amount'],
            beginning_balance=profile.current_balance,
            completed=timezone.now(),
            description=description,
            ending_balance=new_balance,
            transaction_type=Transaction.CREDIT,
            transactee=profile,
        )
        transaction.save()
        profile.current_balance = new_balance
        profile.save()


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


class TransactionBatchDepositView(DepositMixin, FormView):
    form_class = DepositFormSet
    template_name = 'transactions/transaction_batch_deposit.html'
    success_url = '/admin/transactions/deposits/batch'

    def form_valid(self, form):
        count = 0
        try:
            for deposit in form.cleaned_data:
                if deposit:
                    self.create_deposit(deposit)
                    count = count + 1
            messages.success(self.request, 'Successfully processed {} deposits.'.format(count))
        except Exception as e:
            logger.error('An error occured processing a batch deposit: {}'.format(e))
            messages.error(self.request, 'An error occured creating the deposit transactions.')
        return super().form_valid(form)

class TransactionCreateDepositView(DepositMixin, FormView):
    form_class = TransactionDepositForm
    template_name = 'transactions/transaction_single_deposit.html'
    success_url = '/admin/transactions/deposits/today'

    def form_valid(self, form):
        try:
            self.create_deposit(form.cleaned_data)
            profile = Profile.objects.get(user__id=form.cleaned_data['transactee'])
            messages.success(self.request, 'Successfully processed deposit for {}.'.format(profile.name()))
        except Exception as e:
            logger.error('An error occured processing the deposit: {}'.format(e))
            messages.error(self.request, 'An error occured creating the deposit transaction.')
        return super().form_valid(form)


class TransactionCreateOrderView(FormView):
    form_class = TransactionOrderForm
    template_name = 'transactions/transaction_single_order.html'
    success_url = '/admin/transactions/'

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        menu_item_form = MenuLineItemFormSet()
        return self.render_to_response(self.get_context_data(form=form, menu_item_form=menu_item_form))

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        menu_item_form = MenuLineItemFormSet(self.request.POST)
        if (form.is_valid() and menu_item_form.is_valid()):
            return self.form_valid(form, menu_item_form)
        else:
            return self.form_invalid(form, menu_item_form)

    def form_invalid(self, form, menu_item_form):
        return self.render_to_response(self.get_context_data(form=form,menu_item_form=menu_item_form))

    def form_valid(self, form, menu_item_form):
        profile = User.objects.get(pk=form.cleaned_data['transactee']).profile
        new_order = Transaction(
            beginning_balance=profile.current_balance,
            completed=timezone.now(),
            submitted=timezone.now(),
            transactee=profile,
            transaction_type=Transaction.DEBIT
        )
        new_order.save()
        description = ''
        amount = 0
        for item in menu_item_form.cleaned_data:
            menu_item = item['menu_item']
            quantity = item['quantity']
            if description == '':
                description = menu_item.name
            else:
                description = description + ', {}'.format(menu_item.name)
            amount = amount + (menu_item.cost * quantity)
            new_menu_line_item = MenuLineItem.objects.create(menu_item=menu_item, transaction=new_order, quantity=quantity)
        new_order.amount = amount
        new_order.description = description
        new_order.ending_balance = new_order.beginning_balance - amount
        new_order.save()
        profile.current_balance = new_order.ending_balance
        profile.save()
        return super().form_valid(form)


class TransactionExportChecksView(View):
    def get(self, request, *args, **kwargs):
        checks = Transaction.objects.filter(
                description__icontains='Check #',
                transaction_type=Transaction.CREDIT,
            )
        workbook_name = 'check-reconciliation.xlsx'
        if ('year' in self.kwargs) and ('month' in self.kwargs) and ('day' in self.kwargs):
            day = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
            checks = checks.filter(completed__date=day)
            workbook_name = 'check-reconciliation_{}-{}-{}.xlsx'.format(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        if checks:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            bold = workbook.add_format({'bold': True})
            currency_bold = workbook.add_format({'bold': True, 'num_format': '[$$-409]#,##0.00'})
            currency_format = workbook.add_format({'num_format': '[$$-409]#,##0.00'})
            date_format = workbook.add_format({'num_format': 'yyyy-m-d'})
            date_format.set_align('left')
            number_format = workbook.add_format({'align': 'left'})
            worksheet.set_column('A:A', 12)
            worksheet.set_column('B:B', 9)
            worksheet.set_column('C:C', 32)
            worksheet.set_column('D:D', 12)
            worksheet.write(0, 0, 'Date', bold)
            worksheet.write(0, 1, 'Check #', bold)
            worksheet.write(0, 2, 'Student', bold)
            worksheet.write(0, 3, 'Amount', bold)
            row = 1
            col = 0
            for check in checks:
                worksheet.write(row, col, check.completed.date(), date_format)
                worksheet.write(row, col + 1, int(check.description[7:]), number_format)
                worksheet.write(row, col + 2, check.transactee.name())
                worksheet.write(row, col + 3, check.amount, currency_format)
                row += 1
            worksheet.write(row + 1, 0, 'Total', bold)
            worksheet.write(row + 1, 3, '=SUM(D2:D{})'.format(checks.count() + 1), currency_bold)
            workbook.close()
            output.seek(0)
            return FileResponse(output, as_attachment=True, filename=workbook_name)
        else:
            messages.warning(request, 'No checks found to export.')
            return redirect(request.path_info)


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