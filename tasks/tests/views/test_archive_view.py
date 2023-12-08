'''Unit test for toggling archive status'''
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task
from tasks.tests.helpers import reverse_with_next

class ToggleArchiveStatusTestCase(TestCase):
    '''Unit test for toggling archive status'''
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

        # teammate but not current logged in user
        self.teammate_1 = User.objects.get(username="@janedoe")

        # mock team created by user
        self.team = Team.objects.get(pk=1)
        self.team.members.add(self.user, self.teammate_1)

        # other team user does not belong - used to associate other tasks
        self.otherTeam = Team.objects.get(pk=4)

        self.myTeamTask = Task.objects.get(pk=1)
        self.url = reverse('toggle_archive', kwargs={'task_id': self.myTeamTask.id})

        self.otherTeamTask = Task.objects.get(pk=5)
        
    def test_toggle_archive_status_url(self):
        expectedURL = '/toggle_archive/' + str(self.myTeamTask.id)
        self.assertEquals(self.url, expectedURL)

    def test_get_toggle_archive_status_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.post(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_toggle_archive_status_redirects_to_show_team(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.post(self.url, follow=True)
        response_url = reverse('show_team', kwargs={'team_id': self.myTeamTask.author.id})
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_team.html')

    def test_cannot_toggle_archive_status_of_different_team(self):
        self.client.login(username=self.user.username, password='Password123')
        otherTeamTasks = Task.objects.exclude(author=self.team)
        for task in otherTeamTasks:
            # intially false
            self.assertFalse(task.is_archived)
            response = self.client.post(reverse('toggle_archive', kwargs={'task_id': task.id}), follow=True)
            self.assertFalse(task.is_archived)
            response_url = reverse('dashboard')
            # if user gets redirected to dashboard, this means toggling task was unsuccessful
            self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
            self.assertTemplateUsed(response, 'dashboard.html')

