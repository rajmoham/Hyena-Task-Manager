from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from tasks.models import Invitation, Team, User

class InvitationModelTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='Password123')
        self.team = Team.objects.create(author=user, title='Test Team', description='Test description')

    def test_invitation_creation(self):
        invitation = Invitation.objects.create(
            team = self.team,
            email = 'test@example.org',
            status = Invitation.INVITED,
            date_sent = timezone.now()
        )
        self.assertEqual(invitation.email, 'test@example.org')
        self.assertEqual(invitation.status, Invitation.INVITED)
        self.assertEqual(invitation.team, self.team)
