import io
import logging
import xlsxwriter

from collections import Counter
from datetime import date
from typing import Tuple

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import formset_factory
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic import DayArchiveView, TodayArchiveView

from cafeteria.decorators import admin_access_allowed
from menu.models import MenuItem
from profiles.models import Profile
from transactions.models import Transaction, MenuLineItem
from transactions.forms import ItemOrderForm, TransactionDepositForm
from transactions import helpers


logger = logging.getLogger(__file__)


class OrderMixin:
    def create_order(self, order: dict) -> None:
        profile = User.objects.get(id=order["transactee"]).profile
        new_order = Transaction(
            submitted=order["submitted"],
            transactee=profile,
            transaction_type=Transaction.DEBIT,
        )
        new_order.save()
        menu_item = MenuItem.objects.get(id=order["menu_item"])
        MenuLineItem.objects.create(
            menu_item=menu_item, transaction=new_order, quantity=1
        )
        new_order.description = menu_item.name
        new_order.amount = menu_item.cost
        new_order.save()
        self.process_order(new_order)

    def process_order(self, order: Transaction):
        try:
            transactee = order.transactee
            order.beginning_balance = transactee.current_balance
            order.ending_balance = transactee.current_balance - order.amount
            order.completed = timezone.now()
            order.save()
            transactee.current_balance = order.ending_balance
            transactee.save()
        except Exception as e:
            logger.error(
                f"An error occured attempting to process order: {order}\nError message: {e}"
            )

    def process_daily_orders(self, day: date) -> Tuple[bool, str]:
        try:
            orders = Transaction.objects.filter(
                transaction_type=Transaction.DEBIT,
                submitted__date=day,
                completed__date=None,
            )
            if orders:
                for order in orders:
                    self.process_order(order)
                return (
                    True,
                    f'Successfully processed {orders.count()} transactions for {day.strftime("%b %-d, %Y")}.',
                )
            else:
                raise Exception
        except Exception as e:
            logger.error(
                f"When processing transactions, no transactions found for: {day}\nError message: {e}"
            )
            return (
                False,
                f'No transactions found on {day.strftime("%b %-d, %Y")} for processing.',
            )

    def process_single_order(self, id: int) -> Tuple[bool, str]:
        try:
            order = Transaction.objects.get(id=id)
            if not order.completed:
                self.process_order(order)
                return True, f"Successfully processed transaction #{id}."
            else:
                raise Exception
        except Exception as e:
            logger.error(
                f"When processing a transaction, no transaction found for id: {id}\nError message: {e}"
            )
            return (
                False,
                f"Transaction #{id} was either not found or does not need to be processed.",
            )


class TransactionMixin:
    filter = None
    ascending = True
    today = timezone.now
    allow_empty = True
    paginate_by = 20
    date_field = "submitted"

    def get_queryset(self):
        queryset = None
        if self.filter == "deposits":
            queryset = Transaction.objects.filter(transaction_type=Transaction.CREDIT)
        elif self.filter == "orders":
            queryset = Transaction.objects.filter(transaction_type=Transaction.DEBIT)
        else:
            queryset = Transaction.objects.all()
        sort_order = self.request.GET.get("sort") or "ASC"
        self.ascending = sort_order == "ASC"
        sorting = self.request.GET.get("order_by") or "submitted"
        if sorting == "grade":
            sorting = "transactee__grade.value"
        if not self.ascending:
            sorting = "-" + sorting
        self.ascending = not self.ascending
        return queryset.order_by(sorting)


class UserIsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class DeleteTransactionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        transaction = Transaction.objects.get(id=request.POST.get("itemID"))
        try:
            transaction.delete()
            messages.success(self.request, "The transaction was successfully deleted.")
        except Exception as e:
            logger.error("An error occured when deleting a transaction: {}".format(e))
            messages.error(self.request, "There was a problem deleting the transaction")
        return redirect(request.POST.get("path"))


class ExportChecksView(LoginRequiredMixin, UserIsStaffMixin, View):
    def get(self, request, *args, **kwargs):
        deposits = Transaction.objects.filter(
            Q(description__icontains="Check #") | Q(description__icontains="Cash")
        )
        deposits = deposits.filter(transaction_type=Transaction.CREDIT)
        workbook_name = "misc-receipts-form.xlsx"
        if (
            ("year" in self.kwargs)
            and ("month" in self.kwargs)
            and ("day" in self.kwargs)
        ):
            day = date(self.kwargs["year"], self.kwargs["month"], self.kwargs["day"])
            deposits = deposits.filter(completed__date=day)
            workbook_name = f'misc-receipts-form_{self.kwargs["year"]}-{self.kwargs["month"]}-{self.kwargs["day"]}.xlsx'
        else:
            day = "All Deposits"
        if deposits:
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            worksheet.center_horizontally()
            worksheet.fit_to_pages(1, 0)
            worksheet.set_column("A:A", 12)
            worksheet.set_column("B:B", 32)
            worksheet.set_column("C:C", 12)
            worksheet.set_column("D:D", 12)
            worksheet.set_column("E:E", 9)
            worksheet.set_column("F:F", 12)

            general_row_format = workbook.add_format({"font_size": 12})
            center_bold_title = workbook.add_format(
                {"align": "center", "bold": True, "font_size": 14}
            )
            worksheet.merge_range(
                0, 0, 0, 5, "NORTH RALEIGH CHRISTIAN ACADEMY", center_bold_title
            )
            worksheet.merge_range(
                1, 0, 1, 5, "MISCELLANEOUS CAFETERIA RECEIPTS FORM", center_bold_title
            )

            date_bold_title = workbook.add_format(
                {
                    "align": "center",
                    "bold": True,
                    "num_format": "[$-en-US]mmmm d, yyyy;@",
                    "font_size": 12,
                }
            )
            worksheet.merge_range(2, 0, 2, 5, day, date_bold_title)
            worksheet.set_row(2, 18)

            center_bold_header = workbook.add_format(
                {
                    "align": "center",
                    "bold": True,
                    "bottom": 1,
                    "font_size": 12,
                    "left": 1,
                    "right": 1,
                }
            )
            worksheet.write(4, 0, "Date", center_bold_header)
            worksheet.write(4, 1, "Student", center_bold_header)
            worksheet.write(4, 2, "Grade", center_bold_header)
            worksheet.write(4, 3, "Check Amt", center_bold_header)
            worksheet.write(4, 4, "Check #", center_bold_header)
            worksheet.write(4, 5, "Cash", center_bold_header)
            worksheet.set_row(4, 18)

            row = 5
            col = 0
            basic_currency = workbook.add_format(
                {
                    "font_size": 12,
                    "num_format": "[$$-409]#,##0.00",
                    "left": 1,
                    "right": 1,
                }
            )
            basic_date = workbook.add_format(
                {
                    "align": "center",
                    "font_size": 12,
                    "num_format": "yyyy-m-d",
                    "left": 1,
                    "right": 1,
                }
            )
            center = workbook.add_format(
                {"align": "center", "font_size": 12, "left": 1, "right": 1}
            )
            side_border = workbook.add_format({"left": 1, "right": 1})
            for deposit in deposits:
                worksheet.set_row(row, 18, general_row_format)
                worksheet.write(row, col, deposit.completed.date(), basic_date)
                worksheet.write(row, col + 1, deposit.transactee.name(), side_border)
                if deposit.transactee.role == Profile.STAFF:
                    worksheet.write(row, col + 2, "Staff", center)
                else:
                    worksheet.write(
                        row, col + 2, deposit.transactee.grade.value, center
                    )
                if "check #" in deposit.description.lower():
                    worksheet.write(row, col + 3, deposit.amount, basic_currency)
                    worksheet.write(row, col + 4, deposit.description[7:], center)
                    worksheet.write(row, col + 5, "", basic_currency)
                else:
                    worksheet.write(row, col + 3, "", basic_currency)
                    worksheet.write(row, col + 4, "", center)
                    worksheet.write(row, col + 5, deposit.amount, basic_currency)
                row += 1

            bold = workbook.add_format({"bold": True, "font_size": 12})
            worksheet.write(row + 1, 2, "Sub Total", bold)
            currency_bold_single_top = workbook.add_format(
                {
                    "bold": True,
                    "font_size": 12,
                    "num_format": "[$$-409]#,##0.00",
                    "top": 1,
                }
            )
            worksheet.write(
                row + 1,
                3,
                "=SUM(D6:D{})".format(deposits.count() + 5),
                currency_bold_single_top,
            )
            worksheet.write(row + 1, 4, "", currency_bold_single_top)
            worksheet.write(
                row + 1,
                5,
                "=SUM(F6:F{})".format(deposits.count() + 5),
                currency_bold_single_top,
            )
            worksheet.set_row(row + 1, 18, general_row_format)

            worksheet.write(row + 2, 2, "Grand Total", bold)
            grade_total_format = workbook.add_format(
                {
                    "align": "center",
                    "bold": True,
                    "font_size": 12,
                    "num_format": "[$$-409]#,##0.00",
                    "top": 6,
                }
            )
            worksheet.merge_range(
                row + 2,
                3,
                row + 2,
                5,
                "=D{}+F{}".format(row + 2, row + 2),
                grade_total_format,
            )
            worksheet.set_row(row + 2, 18, general_row_format)

            right_aligned = workbook.add_format({"align": "right", "font_size": 12})
            worksheet.set_row(row + 5, 18, general_row_format)
            worksheet.write(row + 5, 0, "Received: ", right_aligned)
            worksheet.write(row + 5, 4, "Receipt #: ", right_aligned)
            underline = workbook.add_format({"bottom": 1})
            worksheet.write(row + 5, 1, "", underline)
            worksheet.write(row + 5, 5, "", underline)

            workbook.close()
            output.seek(0)
            return FileResponse(output, as_attachment=True, filename=workbook_name)
        else:
            messages.warning(request, "No checks found to export.")
            return redirect(request.path_info)


class HomeroomOrdersArchiveView(LoginRequiredMixin, TodayArchiveView):
    template_name = "user/homeroom_orders_today_list.html"
    allow_empty = True
    allow_future = False
    date_field = "submitted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.now
        if self.request.user.profile.role == Profile.STAFF:
            if self.request.user.profile.students.all():
                context["homeroom_teacher"] = True
        return context

    def get_queryset(self):
        return Transaction.objects.filter(
            transactee__in=self.request.user.profile.students.all(),
            transaction_type=Transaction.DEBIT,
        )


class OrderProcessView(LoginRequiredMixin, UserIsStaffMixin, OrderMixin, View):
    def get(self, request, *args, **kwargs):
        success = False
        message = None
        if (
            ("year" in self.kwargs)
            and ("month" in self.kwargs)
            and ("day" in self.kwargs)
        ):
            day = date(self.kwargs["year"], self.kwargs["month"], self.kwargs["day"])
            success, message = self.process_daily_orders(day)
        elif "pk" in self.kwargs:
            success, message = self.process_single_order(self.kwargs["pk"])
        if success and message:
            messages.success(request, message)
        elif message:
            messages.warning(request, message)
        original_url = request.path_info
        elements = original_url.split("/")
        elements.remove("process")
        redirect_url = "/".join(elements)
        return redirect(redirect_url)


class TransactionsDateArchiveView(
    LoginRequiredMixin, UserIsStaffMixin, TransactionMixin, DayArchiveView
):
    template_name = "admin/transactions_list.html"


class TransactionDetailView(
    LoginRequiredMixin, UserIsStaffMixin, TransactionMixin, DetailView
):
    template_name = "admin/transaction_detail.html"


class TransactionListView(
    LoginRequiredMixin, UserIsStaffMixin, TransactionMixin, ListView
):
    template_name = "admin/transactions_list.html"


class TransactionsTodayArchiveView(
    LoginRequiredMixin, UserIsStaffMixin, TransactionMixin, TodayArchiveView
):
    template_name = "admin/transactions_list.html"


class UsersTodayArchiveView(LoginRequiredMixin, TodayArchiveView):
    template_name = "user/user_orders_today_list.html"
    allow_empty = True
    allow_future = False
    date_field = "submitted"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders_open"] = Transaction.accepting_orders()
        if self.request.user.profile.role == Profile.STAFF:
            if self.request.user.profile.students.all():
                context["homeroom_teacher"] = True
        return context

    def get_queryset(self):
        return Transaction.objects.filter(
            transactee=self.request.user.profile, transaction_type=Transaction.DEBIT
        )


class UsersTransactionsArchiveView(LoginRequiredMixin, ListView):
    template_name = "user/user_transactions_list.html"
    allow_empty = True
    allow_future = False

    ascending = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.profile.role == Profile.STAFF:
            if self.request.user.profile.students.all():
                context["homeroom_teacher"] = True
        return context

    def get_queryset(self):
        queryset = Transaction.objects.filter(transactee=self.request.user.profile)
        sort_order = self.request.GET.get("sort") or "ASC"
        self.ascending = sort_order == "ASC"
        sorting = self.request.GET.get("order_by") or "submitted"
        if not self.ascending:
            sorting = "-" + sorting
        self.ascending = not self.ascending
        return queryset.order_by(sorting)


@login_required
@admin_access_allowed
def batch_deposit(request):
    context = {}
    DepositFormSet = formset_factory(TransactionDepositForm, extra=25)
    if request.method == "POST":
        deposit_form = DepositFormSet(request.POST, prefix="deposit")
        if deposit_form.is_valid():
            count = 0
            for deposit in deposit_form.cleaned_data:
                if deposit:
                    try:
                        new_deposit = helpers.create_deposit(deposit)
                        helpers.process_transaction(new_deposit)
                        count = count + 1
                    except Exception as e:
                        logger.exception(
                            "An error occured processing batch deposits: {}".format(e)
                        )
                        messages.error(
                            request, "An error occured processing the batch deposits."
                        )
            messages.success(
                request, "Successfully processed {} deposits.".format(count)
            )
            return redirect("transaction-deposits-batch")
    else:
        context["form"] = DepositFormSet(prefix="deposit")
    return render(request, "admin/transaction_batch_deposit.html", context=context)


@login_required
@admin_access_allowed
def deposit_checklist(request, *args, **kwargs):
    deposits = Transaction.objects.filter(transaction_type=Transaction.CREDIT)
    workbook_name = "misc-deposit-form.xlsx"
    if ("year" in kwargs) and ("month" in kwargs) and ("day" in kwargs):
        day = date(kwargs["year"], kwargs["month"], kwargs["day"])
        deposits = deposits.filter(completed__date=day)
        workbook_name = "check-reconciliation_{}-{}-{}.xlsx".format(
            kwargs["year"], kwargs["month"], kwargs["day"]
        )
    else:
        day = "All Deposits"
    if deposits:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        worksheet.center_horizontally()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_column("A:A", 12)
        worksheet.set_column("B:B", 12)
        worksheet.set_column("C:C", 32)
        worksheet.set_column("D:D", 12)
        worksheet.set_column("E:E", 38)
        worksheet.set_column("F:F", 12)

        general_row_format = workbook.add_format({"font_size": 12})
        center_bold_title = workbook.add_format(
            {"align": "center", "bold": True, "font_size": 14}
        )
        worksheet.merge_range(
            0, 0, 0, 5, "NORTH RALEIGH CHRISTIAN ACADEMY", center_bold_title
        )
        worksheet.merge_range(
            1, 0, 1, 5, "CAFETERIA DEPOSITS CHECKLIST", center_bold_title
        )

        date_bold_title = workbook.add_format(
            {
                "align": "center",
                "bold": True,
                "num_format": "[$-en-US]mmmm d, yyyy;@",
                "font_size": 12,
            }
        )
        worksheet.merge_range(2, 0, 2, 5, day, date_bold_title)
        worksheet.set_row(2, 18)

        center_bold_header = workbook.add_format(
            {
                "align": "center",
                "bold": True,
                "bottom": 1,
                "font_size": 12,
                "left": 1,
                "right": 1,
            }
        )
        worksheet.write(4, 0, "Confirmed", center_bold_header)
        worksheet.write(4, 1, "Date", center_bold_header)
        worksheet.write(4, 2, "Student", center_bold_header)
        worksheet.write(4, 3, "Grade", center_bold_header)
        worksheet.write(4, 4, "Description", center_bold_header)
        worksheet.write(4, 5, "Amount", center_bold_header)
        worksheet.set_row(4, 18)

        row = 5
        col = 1
        basic_currency = workbook.add_format(
            {"font_size": 12, "num_format": "[$$-409]#,##0.00", "left": 1, "right": 1}
        )
        basic_date = workbook.add_format(
            {
                "align": "center",
                "font_size": 12,
                "num_format": "yyyy-m-d",
                "left": 1,
                "right": 1,
            }
        )
        center = workbook.add_format(
            {"align": "center", "font_size": 12, "left": 1, "right": 1}
        )
        side_border = workbook.add_format({"left": 1, "right": 1})
        for deposit in deposits:
            worksheet.set_row(row, 18, general_row_format)
            worksheet.write(row, col, deposit.completed.date(), basic_date)
            worksheet.write(row, col + 1, deposit.transactee.name(), side_border)
            if deposit.transactee.role == Profile.STAFF:
                worksheet.write(row, col + 2, "Staff", center)
            elif deposit.transactee.grade:
                worksheet.write(row, col + 2, deposit.transactee.grade.value, center)
            worksheet.write(row, col + 3, deposit.description, side_border)
            worksheet.write(row, col + 4, deposit.amount, basic_currency)
            row += 1

        bold = workbook.add_format({"align": "right", "bold": True, "font_size": 12})
        worksheet.write(row + 1, 4, "Total", bold)

        grade_total_format = workbook.add_format(
            {
                "align": "center",
                "bold": True,
                "font_size": 12,
                "num_format": "[$$-409]#,##0.00",
                "top": 6,
            }
        )
        worksheet.write(
            row + 1, 5, "=SUM(F6:F{})".format(deposits.count() + 5), grade_total_format
        )
        worksheet.set_row(row + 1, 18, general_row_format)

        workbook.close()
        output.seek(0)
        return FileResponse(output, as_attachment=True, filename=workbook_name)
    else:
        messages.warning(request, "No depostis found to check.")
        return redirect(request.path_info)


@login_required
@admin_access_allowed
def new_single_deposit(request):
    context = {}
    if request.method == "POST":
        deposit_form = TransactionDepositForm(request.POST)
        if deposit_form.is_valid():
            try:
                new_deposit = helpers.create_deposit(deposit_form.cleaned_data)
                helpers.process_transaction(new_deposit)
                profile = deposit_form.cleaned_data["transactee"]
                messages.success(
                    request,
                    "Successfully processed deposit for {}.".format(profile.name()),
                )
                return redirect("profile-detail", profile.id)
            except Exception as e:
                logger.error(
                    f"An exception occured when trying to create a deposit: {e}"
                )
                messages.error(
                    request, "An error occured creating the deposit, please try again."
                )
                return redirect("transaction-deposit-create")
    else:
        context["deposit_form"] = TransactionDepositForm()
    return render(request, "admin/transaction_single_deposit.html", context=context)


@login_required
@admin_access_allowed
def new_single_order(request):
    context = {}
    if request.method == "POST":
        ItemFormSet = formset_factory(ItemOrderForm)
        formset = ItemFormSet(request.POST, prefix="order_form")
        if formset.is_valid():
            ordered_items_list = []
            for item in formset.cleaned_data:
                try:
                    ordered_items_list.append(item["menu_item"])
                except Exception as e:
                    logger.error(
                        f"An error occurred attempting to append ordered items list with item {item}.\nError message: {e}"
                    )

            if len(ordered_items_list) < 1:
                messages.error(request, "You must select at least one item.")
                return redirect("transaction-order-create")
            else:
                transactee = User.objects.get(id=request.POST["transactee"]).profile
                counted_items = Counter(ordered_items_list)
                description = ""
                cost = 0
                for item in counted_items:
                    if description:
                        description = description + ", "
                    description = description + "({}) {}".format(
                        counted_items[item], item.name
                    )
                    cost = cost + (item.cost * counted_items[item])
                try:
                    transaction = Transaction(
                        amount=cost,
                        description=description,
                        transaction_type=Transaction.DEBIT,
                        transactee=transactee,
                    )
                    transaction.save()
                    for item in counted_items:
                        transaction.menu_items.add(
                            item, through_defaults={"quantity": counted_items[item]}
                        )
                    messages.success(
                        request,
                        "Successfully created an order for {}.".format(
                            transactee.name()
                        ),
                    )
                    return redirect("profile-detail", transactee.id)
                except Exception as e:
                    logger.exception(
                        "An exception occured when trying to create a transaction: {}".format(
                            e
                        )
                    )
                    messages.error(request, "An error occured creating the order.")
                    return redirect("transaction-order-create")

    else:
        ItemFormSet = formset_factory(ItemOrderForm)
        context["formset"] = ItemFormSet(prefix="order_form")

    return render(request, "admin/transaction_single_order.html", context=context)
