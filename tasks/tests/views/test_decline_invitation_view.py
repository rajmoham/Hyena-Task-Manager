from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tasks.models import Team, Invitation, User

class DeclineInvitationViewTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = self.user = User.objects.get(username='@johndoe')
        self.team = Team.objects.create(author=self.user, title='Test Team', description='Test description')
        self.invitation = Invitation.objects.create(team=self.team, email=self.user.email)

    def test_decline_invitation(self):
        self.client.login(username=self.user.username, password='Password123')
        initial_member_count = self.team.members.count()
        response = self.client.get(reverse('decline_invitation', args=[self.invitation.id]))
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.DECLINED)
        self.team.refresh_from_db()
        self.assertNotIn(self.user, self.team.members.all())
        self.assertEqual(self.team.members.count(), initial_member_count)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have declined the invitation.")
        self.assertRedirects(response, reverse('list_invitations'))