"""Tests for the seen notifications view."""
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Invitation, Notification
from tasks.tests.helpers import reverse_with_next

class SeenNotificationsViewTestCase(TestCase):
    """Tests for the seen notifications view."""

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
        self.url = reverse('seen_notification', kwargs={'notification_id': self.notification.id})

        # invitation for Jane Doe to join team with pk=1 (John's team)
        self.other_user_invitation = Invitation.objects.get(pk=2)
        self.other_user_notification = Notification.objects.get(pk=2)


    def test_notifications_url(self):
        expectedURL = '/seen_notification/' + str(self.notification.id)
        self.assertEquals(self.url, expectedURL)

    def test_mark_seen_notifications_for_auth_users(self):
        self.client.login(username=self.user.username, password = 'Password123')
        self.assertFalse(self.notification.seen)
        response = self.client.post(self.url)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.seen)
        notifications = Notification.objects.filter(user=self.user)
        # must equal to one since only self.invitation is supposed to be seen
        self.assertEqual(len(notifications), 1)

    def test_user_cannot_mark_notifications_seen_for_other_user(self):
        self.client.login(username=self.user.username, password='Password123')
        self.assertFalse(self.other_user_notification.seen)
        response = self.client.post(reverse('seen_notification', kwargs={'notification_id': self.other_user_notification.id}))
        self.other_user_notification.refresh_from_db()
        self.assertFalse(self.other_user_notification.seen)
        self.notification.refresh_from_db()
        self.assertFalse(self.notification.seen)
        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(len(notifications), 1)

    def test_seen_notifications_redirects_when_not_logged_in(self):
        response = self.client.get(self.url)
        redirect_url = reverse_with_next('log_in', self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

