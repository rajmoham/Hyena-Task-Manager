from django.test import TestCase
from tasks.forms import TeamForm
from tasks.models import Team, User
from django.urls import reverse

class TeamFormTestCase(TestCase):
    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_teams.json',
        'tasks/tests/fixtures/default_task.json',
        'tasks/tests/fixtures/other_tasks.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username="@johndoe")
        self.team = Team.objects.get(pk=1)
        self.url = reverse('edit_team', kwargs={'team_id': self.team.id})
        self.data = {'title': 'Team Name','description': 'Description'}

    def test_team_update_view(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Team.objects.get(pk=1).title, 'Team Name')
        self.assertEqual(Team.objects.get(pk=1).description, 'Description')
    
    def test_valid_form(self):
        data = {'title': 'Test Team', 'description': 'Test Description'}
        form = TeamForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'title': '', 'description': ''}
        form = TeamForm(data=data)
        self.assertFalse(form.is_valid())