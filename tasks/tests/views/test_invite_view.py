from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from tasks.models import Team, Invitation, User
from tasks.forms import TeamInviteForm

class InviteViewTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json',
                'tasks/tests/fixtures/other_users.json',
                'tasks/tests/fixtures/default_team.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.team = Team.objects.get(pk=1)
        self.team.members.add(self.user)
        

    def test_invite_view_without_permission(self):
        """No one except the author of the team can invite a user to the team"""
        other_user = User.objects.get(username='@janedoe')
        self.team.members.add(other_user)
        self.client.login(username=other_user.username, password="Password123")
        response = self.client.get(reverse('invite', args=[self.team.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('show_team', args=[self.team.id]), status_code=302, target_status_code=200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You do not have permission to invite members to this team.")

    def test_invite_view_get(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(reverse('invite', args=[self.team.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')

    def test_invite_view_post_registered_user(self):
        """If a user is registered, the user can be invited to the team"""
        self.client.login(username=self.user.username, password='Password123')
        registered_user = User.objects.get(username='@ericjoker')
        form_data_registered = {'email': registered_user.email}
        response_registered = self.client.post(reverse('invite', args=[self.team.id]), data=form_data_registered)
        self.assertRedirects(response_registered, reverse('show_team', args=[self.team.id]), status_code=302, target_status_code=200)
        self.assertEqual(Invitation.objects.count(), 1)
        invitation_registered = Invitation.objects.first()
        self.assertEqual(invitation_registered.team, self.team)
        self.assertEqual(invitation_registered.email, registered_user.email)
        self.assertEqual(invitation_registered.status, Invitation.INVITED)
        messages_registered = list(get_messages(response_registered.wsgi_request))
        self.assertEqual(len(messages_registered), 1)
        self.assertEqual(str(messages_registered[0]), 'Invitation sent successfully.')

    def test_invite_view_post_non_registered_user(self):
        """Only registered users can be invited to the team"""
        self.client.login(username=self.user.username, password='Password123')
        form_data_non_registered = {'email': 'nonregistered@example.com'}
        response_non_registered = self.client.post(reverse('invite', args=[self.team.id]), data=form_data_non_registered)
        self.assertEqual(response_non_registered.status_code, 200)
        self.assertEqual(Invitation.objects.count(), 0)
