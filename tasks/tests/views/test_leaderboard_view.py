'''Unit test for leaderboard view'''
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task
from tasks.tests.helpers import reverse_with_next

class LeaderboardViewTestCase(TestCase):
    '''Unit test for leaderboard view'''
    
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
        self.teammate_1 = User.objects.get(username="@janedoe")
        self.team = Team.objects.get(pk=1)
        self.team.members.add(self.user, self.teammate_1)

        self.otherTeam = Team.objects.get(pk=4)

        # assign task 1 to user and teammate and assign remaining tasks to user only
        self.myTeamTask1 = Task.objects.get(pk=1)
        self.myTeamTask1.assigned_members.add(self.user, self.teammate_1)
        self.myTeamTask2 = Task.objects.get(pk=2)
        self.myTeamTask2.assigned_members.add(self.user)
        self.myTeamTask3 = Task.objects.get(pk=3)
        self.myTeamTask3.assigned_members.add(self.user)
        self.myTeamTask4 = Task.objects.get(pk=4)
        self.myTeamTask4.assigned_members.add(self.user)
        self.url = reverse('leaderboard', kwargs={'team_id': self.team.id})

        self.otherTeamTask = Task.objects.get(pk=5)
        
    def test_leaderboard_url(self):
        expectedURL = '/leaderboard/' + str(self.team.id)
        self.assertEquals(self.url, expectedURL)

    def test_get_leaderboard_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_leaderboard_renders_show_team(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'show_team.html')

    def test_leaderboard_ranks_user_completed_tasks_in_descending_order(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
 
        # mark tasks 1-4 as complete
        self.myTeamTask1.toggle_task_status()
        self.myTeamTask2.toggle_task_status()
        self.myTeamTask3.toggle_task_status()
        self.myTeamTask4.toggle_task_status()
        
        # user must be on top, teammate below
        members_list = response.context['members']
        user = members_list[0]
        teammate = members_list[1]
        self.assertGreaterEqual(user.total_tasks_completed, teammate.total_tasks_completed)



    

