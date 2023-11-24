from django.test import TestCase
from tasks.models import User, Team, Task
from tasks.forms import TeamForm, TaskForm

class TaskFormTestCase(TestCase):
    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_users.json',
        ]
    def setUp(self):

        super(TestCase, self).setUp()
        self.user = User.objects.get(username = "@johndoe")
        self.team = Team.objects.get(pk=1)

    def test_valid_team_form(self):
        input = {"author": self.team, 'title': 'x'*5, "description": "x*99","due_date": "2040-02-01T12:00:00Z"} 
        form = TaskForm(data=input)
        self.assertTrue(form.is_valid())

    def test_invalid_team_form_without_due_date(self):
        input = {'title': 'x'*200, "description": "x"*88 }
        form = TaskForm(data=input)
        self.assertFalse(form.is_valid())

    def test_invalid_team_form_with_due_date(self):
        input = {'title': 'x'*200, "description": "x"*88,"due_date": "2012-02-01T12:00:00Z"} 
        form = TaskForm(data=input)
        self.assertFalse(form.is_valid())

    
    def test_form_rejects_blank_title(self):
        input = {"author": self.team,'title': '', "description": "x"*88 }
        form = TaskForm(data=input)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_blank_description(self):
        input = {"author": self.user,'title': 'kjhfdkajfh', "description": "" }
        form = TaskForm(data=input)
        self.assertFalse(form.is_valid())

    