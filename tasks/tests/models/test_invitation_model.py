from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from tasks.models import Invitation, Team, User

class InvitationModelTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='Password123')
        self.team = Team.objects.create(author=user, title='Test Team', description='Test description')
        self.invitation = Invitation.objects.create(
            team = self.team,
            email = 'test@example.org',
            status = Invitation.INVITED,
            date_sent = timezone.now()
        )

    def test_invitation_creation(self):
        self.assertEqual(self.invitation.email, 'test@example.org')
        self.assertEqual(self.invitation.status, Invitation.INVITED)
        self.assertEqual(self.invitation.team, self.team)

    def test_team_is_not_null(self):
        self.assertIsNotNone(self.invitation.team)

    def test_date_sent_is_not_null(self):
        self.assertIsNotNone(self.invitation.date_sent)

    def test_email_cannot_be_null(self):
        self.assertIsNotNone(self.invitation.email)

    def test_status_cannot_be_null(self):
        self.assertIsNotNone(self.invitation.status)
        



