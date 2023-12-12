"""Tests of the accept invitations view."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tasks.models import Team, Invitation, User

class AcceptInviteViewTestCase(TestCase):
    """Tests of the accept invitations view."""

    fixtures = [
            'tasks/tests/fixtures/default_user.json',
            'tasks/tests/fixtures/other_users.json',
            'tasks/tests/fixtures/default_team.json',
            'tasks/tests/fixtures/other_teams.json',
            'tasks/tests/fixtures/default_invitations.json'
        ]

    def setUp(self):
        self.user = self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.team = Team.objects.get(pk=4)

        # invitation for John Doe
        self.invitation = Invitation.objects.get(pk=1)
        self.url = reverse('accept_invitation', args=[self.invitation.id])

    def test_decline_invitation_url(self): 
        self.assertEqual(self.url,'/invitations/accept/' + str(self.invitation.id)+"/")

    def test_accept_invitation(self):
        self.client.login(username=self.user.username, password='Password123')
        initial_member_count = self.team.members.count()
        response = self.client.get(reverse('accept_invitation', args=[self.invitation.id]))
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.ACCEPTED)
        self.team.refresh_from_db()
        self.assertIn(self.user, self.team.members.all())
        self.assertEqual(self.team.members.count(), initial_member_count + 1)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have joined the team!")
        self.assertRedirects(response, reverse('notifications'))

    def test_unauthorized_accept_invitation(self):
        self.client.login(username=self.other_user.username, password='Password123')
        response = self.client.post(reverse('accept_invitation', args=[self.invitation.id]))
        self.assertEqual(response.status_code, 404)
