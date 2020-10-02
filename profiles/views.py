from functools import reduce
import operator

from django.contrib.auth.models import User
from django.db.models import Q
from django.views.generic import DetailView, ListView

from profiles.models import Profile
from transactions.models import Transaction


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/admin/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = kwargs['object']
        context['transactions'] = Transaction.objects.filter(transactee=profile).order_by('-submitted')        
        context['students'] = profile.students.all()
        return context


class ProfileListView(ListView):
    model = Profile
    template_name = 'profiles/admin/profiles_list.html'


class ProfileSearchResultsView(ListView):
    model = Profile
    template_name = 'profiles/admin/profiles_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = True
        return context

    def get_queryset(self): # new
        query = self.request.GET.get('q')
        if query:
            query_list = query.split()
            result = Profile.objects.filter(
                reduce(operator.or_, (Q(user__first_name__icontains=q) for q in query_list)) |
                reduce(operator.or_, (Q(user__last_name__icontains=q) for q in query_list))
            )
            return result
        else:
            return Profile.objects.none()