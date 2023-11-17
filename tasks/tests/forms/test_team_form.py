from django.test import TestCase
from tasks.models import User, Team
from tasks.forms import TeamForm

class TeamFormTestCase(TestCase):

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username = "@johndoe")

    def test_valid_team_form(self):
        input = {"author": self.user, 'title': 'x'*5, "description": "x*99", "created_at": "2030-02-01T12:00:00Z"}
        form = TeamForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_team_form(self):
        input = {'title': 'x'*200, "description": "x"*88 }
        form = TeamForm(data=input)
        self.assertFalse(form.is_valid())

    def test_form_rejects_blank_title(self):
        input = {"author": self.user,'title': '', "description": "x"*88, "created_at": "2030-02-01T12:00:00Z"}
        form = TeamForm(data=input)
        self.assertFalse(form.is_valid())

    def test_form_accepts_blank_description(self):
        input = {"author": self.user,'title': 'kjhfdkajfh', "description": "", "created_at": "2030-02-01T12:00:00Z"}
        form = TeamForm(data=input)
        self.assertTrue(form.is_valid())