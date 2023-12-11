"""Tests for the notifications view."""
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Invitation, Notification
from tasks.tests.helpers import reverse_with_next

class NotificationsViewTestCase(TestCase):
    """Tests for the notifications view."""

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_teams.json',
        'tasks/tests/fixtures/default_invitations.json',
        'tasks/tests/fixtures/default_notifications.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username="@johndoe")
        self.other_user = User.objects.get(username="@janedoe")
        self.team = Team.objects.get(pk=1)
        self.team.members.add(self.user)

        # invitation for John Doe to join team with pk=4
        self.invitation = Invitation.objects.get(pk=1)
        self.notification = Notification.objects.get(pk=1)
        self.url = reverse('notifications')

        # invitation for Jane Doe to join team with pk=1 (John's team)
        self.other_user_invitation = Invitation.objects.get(pk=2)
        self.other_user_notification = Notification.objects.get(pk=2)

    def test_notifications_url(self):
        expectedURL = '/notifications'
        self.assertEquals(self.url, expectedURL)

    def test_display_notifications_for_auth_users(self):
        self.client.login(username=self.user.username, password = 'Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Noti Test 1")
        notifications = Notification.objects.filter(user=self.user)
        # must equal to one since only self.invitation is supposed to be seen
        self.assertEqual(len(notifications), 1)

    def test_notifications_view_displays_notifications_for_user_only(self):
        self.client.login(username=self.user.username, password = 'Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Noti Test 2")

    def test_get_notifications_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_notification_is_created_for_invitations_without_notifications_initially(self):
        self.client.login(username=self.user.username, password = 'Password123')

        # invitation object where notification object is not created with it

        other_team_invited = Team.objects.get(pk=5)
        invitation_without_notification_object = Invitation.objects.create(team=other_team_invited, email="johndoe@example.org", status=Invitation.INVITED)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Invitation to join Team Test5")
        notifications = Notification.objects.filter(user=self.user)
        # must equal to two since only self.invitation and the newly created invite is supposed to be seen
        self.assertEqual(len(notifications), 2)
