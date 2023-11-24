from django.test import TestCase
from django.urls import reverse
from tasks.models import Team
from tasks.views import TeamUpdateView

class TeamUpdateViewTestCase(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name='Team A', description='A team')

    def test_team_update_view_updates_details(self):
        # Simulate a POST request to the edit_team URL with updated data
        response = self.client.post(reverse('edit_team', args=[self.team.id]), {'name': 'Team B', 'description': 'B team'})

        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)

        # Check if the team details have been updated in the database
        team = Team.objects.get(id=self.team.id)
        self.assertEqual(team.name, 'Team B')
        self.assertEqual(team.description, 'B team')
