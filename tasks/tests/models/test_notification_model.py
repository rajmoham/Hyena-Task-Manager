from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import User, Notification, Invitation, Team
from django.utils import timezone
from datetime import datetime

class NotificationTest(TestCase):

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/default_task.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/other_teams.json',
        'tasks/tests/fixtures/other_tasks.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.notification = Notification.objects.create(
            title='Title',
            description="Description",
            created_at=datetime.fromisoformat("2004-02-01T12:00:00Z"),
            user = self.user,
            actionable=True,
            seen=False,
        )

    def test_valid_message(self):
        try:
            self.notification.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_title_must_not_be_blank(self):
        self.notification.title = ''
        with self.assertRaises(ValidationError):
            self.notification.full_clean()

    def test_description_can_be_blank(self):
        self.notification.description = ''
        self.notification.full_clean()

    def test_created_at_is_not_null(self):
        self.assertIsNotNone(self.notification.created_at)
    
    def test_user_is_not_null(self):
        self.assertIsNotNone(self.notification.user)
    
    def test_valid_notification_with_invitation(self):
        invitation = Invitation.objects.create(
            team=Team.objects.create(author=self.user, title='Test Team', description='Test description'),
            email = 'test@example.org',
            status = Invitation.INVITED,
            date_sent = timezone.now()
        )
        self.notification.invitation = invitation
        self.notification.full_clean()

    def test_notifcation_mark_as_seen_works(self):
        self.assertFalse(self.notification.seen)
        self.notification.mark_as_seen()
        self.assertTrue(self.notification.seen)
