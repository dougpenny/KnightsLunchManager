from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from profiles.models import Profile
from django.contrib.auth.models import User


# class IndexView(generic.ListView):
#     template_name = 'polls/index.html'
#     context_object_name = 'latest_question_list'

#     def get_queryset(self):
#         """Return the last five published questions."""
#         return Question.objects.order_by('-pub_date')[:5]


# class DetailView(generic.DetailView):
#     model = Profile
#     template_name = 'polls/detail.html'



# class ProfileAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         if not self.request.user.is_authenticated:
#             return Profile.objects.none()
#         queryset = Profile.objects.filter(Q(role=Profile.STUDENT) | Q(role=Profile.STAFF))
#         if self.q:
#             queryset = queryset.filter(Q(user__first_name__icontains=self.q) | Q(user__last_name__icontains=self.q))
#         return queryset