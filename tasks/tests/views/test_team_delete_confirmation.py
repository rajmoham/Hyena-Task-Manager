from django.test import TestCase
from django.urls import reverse
from tasks.forms import TeamForm
from tasks.models import Team, User
from tasks.views import TeamUpdateView

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.messages import constants as messages
from unittest.mock import patch
from tasks.models import Team

class TeamDeleteConfirmation(TestCase):
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
        self.url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.data = {'title': 'Team Name','description': 'Description'}
    
    def test_confirmation_popup(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to submit?")

    def test_team_delete(self):
        self.client.login(username='testuser', password='12345')
        team_count_before = Team.objects.count()
        response = self.client.post(reverse('team_delete', args=[self.team.pk]))   
        team_count_after = Team.objects.count()
        self.assertEqual(team_count_after, team_count_before-1)
        

    


    