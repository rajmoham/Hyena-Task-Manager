""" Tests of the Dashboard view """
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task
from tasks.tests.helpers import reverse_with_next
from django.db.models import Q
from datetime import datetime


class DashboardViewTestCase(TestCase):
    """ Tests of the Dashboard view """

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_teams.json',
        'tasks/tests/fixtures/default_task.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username="@johndoe")

        # teammate but not current logged in user
        self.teammate_1 = User.objects.get(username="@janedoe")

        # other registered user in the system but not in the same team
        self.other_registered_user = User.objects.get(username="@petrapickles")
        
        self.url = reverse('dashboard')

        # mock team created by user
        self.team_own1 = Team.objects.get(pk=1)
        self.team_own1.members.add(self.user, self.teammate_1)

        self.team_own2 = Team.objects.get(pk=2)
        self.team_own2.members.add(self.user, self.teammate_1)

        self.team_own3 = Team.objects.get(pk=3)
        self.team_own3.members.add(self.user, self.teammate_1)
        
        # mock team created by team mate
        self.team_other_invited = Team.objects.get(pk=7)
        self.team_other_invited.members.add(self.user, self.teammate_1)

        #mock team created by other user but did not invite current user
        self.team_other_not_invited = Team.objects.get(pk=6)
        self.team_other_not_invited.members.add(self.other_registered_user)
        self.task = Task.objects.get(pk=1)
        

    def test_dashboard_url(self):
        self.assertEqual(self.url, '/dashboard/')

    def test_dashboard_displays_users_first_name(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, self.user.username)

    def test_dashboard_displays_all_user_teams(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user_teams = Team.objects.filter(members=self.user) 
        for team in user_teams:
            self.assertContains(response, team.title)

    def test_dashboard_displays_teams_user_is_not_creator_but_just_member(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user_teams = Team.objects.filter(Q(members=self.user) & ~Q(author=self.user)) 
        for team in user_teams:
            self.assertContains(response, team.title)

    def test_dashboard_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_dashboard_does_not_display_teams_user_is_not_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        other_teams_without_current_user = Team.objects.exclude(members=self.user) 
        for team in other_teams_without_current_user:
            self.assertNotContains(response, team.title)

    def test_dashboard_displays_each_team_member_is_in_only_once2(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        my_teams = Team.objects.filter(members=self.user)
        self.assertTrue('user_teams' in response.context)
        response_user_teams = response.context['user_teams']
        self.assertEqual(set(response_user_teams), set(my_teams))
        self.assertEqual(len(response_user_teams), len(my_teams))

    # TO DO: test for notifications once feature is done

    def test_dashboard_displays_tasks(self):
        self.client.login(username=self.user.username, password="Password123")
        self.task.assigned_members.add(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, self.task.title)

    def test_dashboard_displays_overdue_tasks(self):
        self.client.login(username=self.user.username, password="Password123")
        self.task.assigned_members.add(self.user)
        self.task.due_date = datetime.fromisoformat("2004-02-01T12:00:00+00:00")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, self.task.title)

    def test_dashboard_does_not_display_tasks_not_assigned_to_user(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertNotContains(response, self.task.title)
        
    



