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
        context['transactions'] = Transaction.objects.filter(transactee=kwargs['object']).order_by('-submitted')
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
        return Profile.objects.filter(
            Q(user__first_name__icontains=query) | Q(user__last_name__icontains=query)
        )