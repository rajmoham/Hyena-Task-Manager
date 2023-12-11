from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from tasks.views import LoginProhibitedMixin, TeamAuthorProhibitedMixin, TeamMemberProhibitedMixin
from tasks.models import Team, User

class LoginProhibitedMixinTestCase(TestCase):
	def test_login_prohibited_throws_exception_when_not_configured(self):
		mixin = LoginProhibitedMixin()
		with self.assertRaises(ImproperlyConfigured):
			mixin.get_redirect_when_logged_in_url()

class TeamAuthorProhibitedMixinTestCase(TestCase):
	def test_team_author_throws_exception_when_not_configured(self):
		mixin = TeamAuthorProhibitedMixin()
		with self.assertRaises(ImproperlyConfigured):
			mixin.get_redirect_when_not_team_author()

class TeamMemberProhibitedMixinTestCase(TestCase):
	def test_team_member_throws_exception_when_not_configured(self):
		mixin = TeamMemberProhibitedMixin()
		with self.assertRaises(ImproperlyConfigured):
			mixin.get_redirect_when_not_team_member()