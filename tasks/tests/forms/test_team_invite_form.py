from django.test import TestCase
from tasks.models import User, Team, Invitation
from tasks.forms import TeamInviteForm

class TeamInviteFormTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.org', password='Password123')
        self.other_user = User.objects.create_user(username='otheruser', email='otheruser@example.org', password='Password123')
        self.other_user2 = User.objects.create_user(username='otheruser2', email='invited@example.org', password='Password123')
        self.team = Team.objects.create(title='Test Team', author=self.user)
        self.team.members.add(self.other_user)
        self.invitation = Invitation.objects.create(team=self.team, email='invited@example.org', status=Invitation.INVITED)
        self.form_data = {'email': 'test@example.org'}

    def test_registered_email(self):
        form = TeamInviteForm(data=self.form_data, team=self.team)
        self.assertTrue(form.is_valid())

    def test_invalid_email_not_registered(self):
        form_data = {'email': 'invalid@example.com'}
        form = TeamInviteForm(data=form_data, team=self.team)
        self.assertFalse(form.is_valid())
        self.assertIn('No user is registered with this email address.', form.errors['email'])

    def test_user_already_in_team(self):
        form = TeamInviteForm(data={'email': 'otheruser@example.org'}, team=self.team)
        self.assertFalse(form.is_valid())
        self.assertIn('User already in the team.', form.errors['email'])

    def test_user_already_invited(self):
        form = TeamInviteForm(data={'email': 'invited@example.org'}, team=self.team)
        self.assertFalse(form.is_valid())
        self.assertIn('This user has already been invited to the team.', form.errors['email'])
