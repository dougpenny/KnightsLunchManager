import logging
import operator
import uuid

from functools import reduce

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import resolve, reverse_lazy
from django.views.generic import DetailView, ListView

from constance import config

from cafeteria.decorators import admin_access_allowed
from cafeteria.pdfgenerators import lunch_card_for_users
from profiles.models import Profile
from transactions import helpers
from transactions.models import Transaction

logger = logging.getLogger(__file__)


class ProfileMixin:
    allow_empty = True
    ascending = True
    filter = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filter
        return context

    def get_queryset(self):
        if self.filter == 'debt':
            queryset = Profile.objects.filter(active=True).filter(current_balance__lt=0)
        elif self.filter == 'search':
            query = self.request.GET.get('q')
            include_inactive = False
            if query:
                if query[0] == '/':
                    include_inactive = True
                    query = query[1:]
                query_list = query.split()
                queryset = Profile.objects.filter(
                    reduce(operator.or_, (Q(user__first_name__icontains=q) for q in query_list)) |
                    reduce(operator.or_, (Q(user__last_name__icontains=q) for q in query_list))
                )
                if not include_inactive:
                    queryset = queryset.filter(active=True)
            else:
                queryset = Profile.objects.none()
        else:
            queryset = Profile.objects.filter(active=True)
        sort_order = self.request.GET.get('sort') or 'ASC'
        self.ascending = sort_order == 'ASC'
        sorting = self.request.GET.get('order_by') or 'current_balance'
        if sorting == 'name':
            sorting = 'user__last_name'
        if not self.ascending:
            sorting = '-' + sorting
        self.ascending = not self.ascending
        return queryset.order_by(sorting)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'admin/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = kwargs['object']
        context['transactions'] = Transaction.objects.filter(
            transactee=profile).order_by('-submitted')
        context['students'] = profile.students.all()
        return context


class ProfileListView(LoginRequiredMixin, ProfileMixin, ListView):
    model = Profile
    template_name = 'admin/profiles_list.html'


class ProfileSearchResultsView(LoginRequiredMixin, ProfileMixin, ListView):
    model = Profile
    template_name = 'admin/profiles_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = True
        context['query'] = self.request.GET.get('q')
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
    if request.method == 'POST':
        pass
    else:
        context = {}
        context['inactive'] = True
        context['object_list'] = Profile.objects.filter(pending=True)

    return render(request, 'admin/profiles_list.html', context=context)


@login_required
@admin_access_allowed
def make_inactive(request, pk):
    try:
        profile = Profile.objects.get(id=pk)
        # Zero out the balance
        balance = profile.current_balance
        description = "Balance transferred to the Business Office"
        transaction_type = Transaction.DEBIT
        if balance < 0:
            description = "Balance settled by the Business Office"
            transaction_type = Transaction.CREDIT
        transaction = Transaction(
            amount=abs(balance),
            description=description,
            transaction_type=transaction_type,
            transactee=profile
        )
        transaction.save()
        helpers.process_transaction(transaction)

        # Reset lunch card ID and make user inactive
        profile.lunch_uuid = uuid.uuid4()
        profile.cards_printed = 0
        profile.active = False
        profile.save()
        profile.user.is_active = False
        profile.user.save()
        messages.info(request, 'Successfully set {} as inactive.'.format(profile.name()))
        return redirect('admin')
    except:
        logger.info('An error occured when trying to set {} as inactive'.format(profile.name()))
        messages.error(request, 'An error occured trying to set {} as inactive'.format(profile.name()))
    
    return redirect('profile-detail', args=[pk])


@login_required
@admin_access_allowed
def new_individual_card(request, pk):
    if request.method == 'POST':
        if 'waive-fee' in request.POST:
            cost = 0
        else:
            cost = config.NEW_CARD_FEE
        try:
            profile = Profile.objects.get(id=pk)
            transaction = Transaction(
                        amount=cost,
                        description='Replacement lunch card.',
                        transaction_type=Transaction.DEBIT,
                        transactee=profile)
            transaction.save()
            helpers.process_transaction(transaction)
            profile.lunch_uuid = uuid.uuid4()
            profile.save()
            return lunch_card_for_users([profile])
        except Exception as e:
            if transaction:
                transaction.delete()
            logger.info('An error occured trying to print a new lunch card: {}'.format(e))
            messages.error(request, 'An error occured trying to print the new lunch card.')

    return HttpResponseRedirect(reverse_lazy('profile-detail', args=[pk]))