import os, unicodedata

from django.utils import timezone

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from powerschool.powerschool import Powerschool
from profiles.models import Profile


def generate_username(email):
	# Using Python 3 and Django 1.11+, usernames can contain alphanumeric
	# (ascii and unicode), _, @, +, . and - characters. So we normalize
	# it and slice at 150 characters.
	return unicodedata.normalize('NFKC', email)[:150]


def powerschool_logout(request):
	redirect_url = os.getenv('POWERSCHOOL_URL') + 'guardian/home.html?ac=logoff'
	return redirect_url


class PowerSchoolGuardianOIDC(OIDCAuthenticationBackend):
	def update_students(self, profile):
		client = Powerschool()
		students = client.students_for_guardian(profile.user_dcid)
		profile.children.clear()
		for student in students:
			try:
				profile.children.add(Profile.objects.get(student_dcid=student))
			except:
				pass


	def create_user(self, claims):
		user = super(PowerSchoolGuardianOIDC, self).create_user(claims)
		user.first_name = claims.get('given_name', '')
		user.last_name = claims.get('family_name', '')
		user.save()
		profile = Profile(
			last_sync = timezone.now(),
			role = Profile.GUARDIAN,
			active = True,
			user_dcid = claims.get('ps_dcid'),
			user = user
		)
		profile.save()
		self.update_students(profile)
		
		return user
		

	def update_user(self, user, claims):
		user.first_name = claims.get('given_name', '')
		user.last_name = claims.get('family_name', '')
		user.save()
		if user.profile:
			user.profile.last_sync = timezone.now()
			user.profile.save()
		else:
			profile = Profile(
				last_sync = timezone.now(),
				role = Profile.GUARDIAN,
				active = True,
				user_dcid = claims.get('ps_dcid'),
				user = user
			)
			profile.save()
		self.update_students(user.profile)
		
		return user
