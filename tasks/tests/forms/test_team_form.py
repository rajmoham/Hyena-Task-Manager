from django.test import TestCase
from tasks.models import User, Team
from tasks.forms import TeamForm

class TeamFormTestCase(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )

    def test_valid_team_form(self):
        input = {'text': 'x'*200 }
        form = TeamForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_team_form(self):
        input = {'text': 'x'*600 }
        form = TeamForm(data=input)
        self.assertFalse(form.is_valid())