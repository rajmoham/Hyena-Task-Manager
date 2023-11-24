from django.test import TestCase
from django.core.exceptions import ValidationError
from tasks.models import User
from tasks.forms import TeamInviteForm

class TeamInviteFormTestCase(TestCase):
    def setUp(self):
        self.form_data = {'email': 'test@example.com'}
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='Password123')

    def test_registered_email(self):
        form = TeamInviteForm(data=self.form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_email_not_registered(self):
        form_data = {'email': 'invalid@example.com'}
        form = TeamInviteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('No user is registered with this email address.', form.errors['email'])
