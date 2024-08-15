import io
import logging
import operator
import uuid
import xlsxwriter

from functools import reduce

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView

from constance import config

from cafeteria.decorators import admin_access_allowed
from cafeteria.pdfgenerators import lunch_card_for_users
from profiles.models import Profile
from profiles.helpers import process_inactive
from transactions import helpers
from transactions.models import Transaction

logger = logging.getLogger(__file__)


class ProfileMixin:
    allow_empty = True
    ascending = True
    filter = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        return context

    def get_queryset(self):
        if self.filter == "debt":
            queryset = Profile.objects.filter(active=True).filter(current_balance__lt=0)
        elif self.filter == "search":
            query = self.request.GET.get("q")
            include_inactive = False
            if query:
                if query[0] == "/":
                    include_inactive = True
                    query = query[1:]
                query_list = query.split()
                queryset = Profile.objects.filter(
                    reduce(
                        operator.or_,
                        (Q(user__first_name__icontains=q) for q in query_list),
                    )
                    | reduce(
                        operator.or_,
                        (Q(user__last_name__icontains=q) for q in query_list),
                    )
                )
                if not include_inactive:
                    queryset = queryset.filter(active=True)
            else:
                queryset = Profile.objects.none()
        else:
            queryset = Profile.objects.filter(active=True)
        sort_order = self.request.GET.get("sort") or "ASC"
        self.ascending = sort_order == "ASC"
        sorting = self.request.GET.get("order_by") or "current_balance"
        if sorting == "name":
            sorting = "user__last_name"
        if not self.ascending:
            sorting = "-" + sorting
        self.ascending = not self.ascending
        return queryset.order_by(sorting)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "admin/profile_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = kwargs["object"]
        context["transactions"] = Transaction.objects.filter(
            transactee=profile
        ).order_by("-submitted")
        context["students"] = profile.students.all()
        return context


class ProfileListView(LoginRequiredMixin, ProfileMixin, ListView):
    model = Profile
    template_name = "admin/profiles_list.html"


class ProfileSearchResultsView(LoginRequiredMixin, ProfileMixin, ListView):
    model = Profile
    template_name = "admin/profiles_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = True
        context["query"] = self.request.GET.get("q")
        return context

    # def get_queryset(self):  # new
    #     query = self.request.GET.get('q')
    #     if query:
    #         query_list = query.split()
    #         result = Profile.objects.filter(
    #             reduce(operator.or_, (Q(user__first_name__icontains=q) for q in query_list)) |
    #             reduce(operator.or_, (Q(user__last_name__icontains=q) for q in query_list))
    #         )
    #         return result
    #     else:
    #         return Profile.objects.none()


@login_required
@admin_access_allowed
def pending_inactive_students(request):
    if request.method == "POST":
        pass
    else:
        context = {}
        context["inactive"] = True
        context["object_list"] = Profile.objects.filter(pending=True)

    return render(request, "admin/profiles_list.html", context=context)


@login_required
@admin_access_allowed
def set_inactive(request, pk):
    profile = Profile.objects.get(id=pk)
    try:
        profile = process_inactive(profile)
        if profile:
            messages.info(
                request, "Successfully set {} as inactive.".format(profile.name())
            )
            return redirect("admin")
    except Exception as e:
        logger.info(
            f"An exception occured when trying to set {profile} as inactive.\nException: {e}"
        )
        messages.error(
            request,
            "An error occured trying to set {} as inactive".format(profile.name()),
        )

    return redirect("profile-detail", args=[pk])


@login_required
@admin_access_allowed
def set_all_inactive(request):
    profiles = Profile.objects.filter(pending=True)
    try:
        count = 0
        for profile in profiles:
            profile = process_inactive(profile)
            if profile:
                count = count + 1

        messages.info(request, f"Successfully set {count} users as inactive.")
        return redirect("admin")
    except Exception as e:
        logger.info(
            "An exception occured when trying to set users as inactive.\nException: {e}"
        )
        messages.error(request, "An error occured trying to set users as inactive")

    return redirect("pending-inactive")


@login_required
@admin_access_allowed
def new_individual_card(request, pk):
    if request.method == "POST":
        if "waive-fee" in request.POST:
            cost = 0
        else:
            cost = config.NEW_CARD_FEE
        try:
            profile = Profile.objects.get(id=pk)
            transaction = Transaction(
                amount=cost,
                description="Replacement lunch card.",
                transaction_type=Transaction.DEBIT,
                transactee=profile,
            )
            transaction.save()
            helpers.process_transaction(transaction)
            profile.lunch_uuid = uuid.uuid4()
            profile.save()
            return lunch_card_for_users([profile])
        except Exception as e:
            if transaction:
                transaction.delete()
            logger.info(
                f"An exception occured trying to print a new lunch card for: {profile}\nException: {e}"
            )
            messages.error(
                request, "An error occured trying to print the new lunch card."
            )

    return HttpResponseRedirect(reverse_lazy("profile-detail", args=[pk]))


@login_required
@admin_access_allowed
def reconciliation_report(request) -> FileResponse:
    debtors = Profile.objects.filter(active=True).filter(pending=True)
    workbook_name = "reconciliation-report.xlsx"
    if debtors:
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()
        worksheet.center_horizontally()
        worksheet.fit_to_pages(1, 0)
        worksheet.set_column("A:A", 32)
        worksheet.set_column("B:B", 12)
        worksheet.set_column("C:C", 12)

        general_row_format = workbook.add_format({"font_size": 12})
        center_bold_title = workbook.add_format(
            {"align": "center", "bold": True, "font_size": 14}
        )
        worksheet.merge_range(
            0, 0, 0, 2, "NORTH RALEIGH CHRISTIAN ACADEMY", center_bold_title
        )
        worksheet.merge_range(1, 0, 1, 2, "RECONCILIATION REPORT", center_bold_title)
        worksheet.merge_range(2, 0, 2, 2, config.CURRENT_YEAR, center_bold_title)
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
        worksheet.write(4, 0, "Student", center_bold_header)
        worksheet.write(4, 1, "Grade", center_bold_header)
        worksheet.write(4, 2, "Balance", center_bold_header)
        worksheet.set_row(4, 18)

        row = 5
        col = 0
        basic_currency = workbook.add_format(
            {"font_size": 12, "num_format": "[$$-409]#,##0.00", "left": 1, "right": 1}
        )
        center = workbook.add_format(
            {"align": "center", "font_size": 12, "left": 1, "right": 1}
        )
        side_border = workbook.add_format({"left": 1, "right": 1})
        for profile in debtors:
            worksheet.set_row(row, 18, general_row_format)
            worksheet.write(row, col, profile.name(), side_border)
            if profile.role == Profile.STAFF:
                worksheet.write(row, col + 1, "Staff", center)
            elif profile.grade:
                worksheet.write(row, col + 1, profile.grade.value, center)
            worksheet.write(row, col + 2, profile.current_balance, basic_currency)
            row += 1

        bold = workbook.add_format({"align": "right", "bold": True, "font_size": 12})
        worksheet.write(row + 1, 1, "Total", bold)

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
            row + 1, 2, "=SUM(C6:C{})".format(debtors.count() + 5), grade_total_format
        )
        worksheet.set_row(row + 1, 18, general_row_format)

        workbook.close()
        output.seek(0)
        return FileResponse(output, as_attachment=True, filename=workbook_name)
    else:
        messages.warning(request, "No debtors found for reconciliation.")
        return redirect(request.path_info)
