from functools import reduce
import operator

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import resolve
from django.views.generic import DetailView, ListView

from profiles.models import Profile
from transactions.models import Transaction


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
            queryset = Profile.objects.filter(current_balance__lt=0)
        elif self.filter == 'search':
            query = self.request.GET.get('q')
            if query:
                query_list = query.split()
                queryset = Profile.objects.filter(
                    reduce(operator.or_, (Q(user__first_name__icontains=q) for q in query_list)) |
                    reduce(operator.or_, (Q(user__last_name__icontains=q) for q in query_list))
                )
            else:
                queryset = Profile.objects.none()
        else:
            queryset = Profile.objects.all()
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
