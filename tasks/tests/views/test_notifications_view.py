from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Invitation, Notification

class NotificationsViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com', 'Password123')
        self.other_user = User.objects.create_user('otheruser', 'other@example.com', 'Password123')
        self.team = Team.objects.create(author=self.user, title='Test Team')
        self.invitation = Invitation.objects.create(team=self.team, email=self.user.email, status=Invitation.INVITED)

    def test_display_notifications_for_auth_users(self):
        self.client.login(username='user', password = 'Password123')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invitation to join Test Team")

    def test_generate_notification_for_new_invitation(self):
        self.client.login(username='user', password = 'Password123')
        Notification.objects.filter(user = self.user, invitation=self.invitation).delete()
        self.client.get(reverse('notifications'))
        notification_exists = Notification.objects.filter(user=self.user, invitation=self.invitation).exists()
        self.assertTrue(notification_exists)
