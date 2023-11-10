""" Tests of the Dashboard view """
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User
from tasks.tests.helpers import reverse_with_next


class DashboardViewTestCase(TestCase):
    """ Tests of the Dashboard view """

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username="@johndoe")

        # teammate but not current logged in user
        self.teammate_1 = User.objects.get(username="@janedoe")
        
        self.url = reverse('dashboard')

        # mock team created by user
        self.team_own1 = Team.objects.create(
            author=self.user,
            title="TeamA",
            description="This is my team",
        )
        self.team_own1.members.add(self.user, self.teammate_1)

        self.team_own2 = Team.objects.create(
            author=self.user,
            title="TeamAA",
            description="This is my team",
        )
        self.team_own2.members.add(self.user, self.teammate_1)
        '''
        - TO BE IMPLEMENTED AFTER USER INVITE FEATURE IS DONE: -
        # mock team created by team mate
        self.team_other = Team.objects.create(
            author=self.teammate_1,
            title="TeamB",
            description="This is my team",
        )
        self.team_other.members.add(self.user, self.teammate_1)
        '''

    def test_dashboard_url(self):
        self.assertEqual(self.url, '/dashboard/')

    def test_dashboard_displays_username(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, self.user.username)

    def test_dashboard_displays_teams(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, self.team_own1.title)
    
    def test_dashboard_displays_teams(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, self.team_own2.title)

    def test_dashboard_displays_all_user_teams(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user_teams = Team.objects.filter(members=self.user) 
        for team in user_teams:
            self.assertContains(response, team.title)

    def test_dashboard_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    '''
    - TO BE IMPLEMENTED AFTER USER INVITE FEATURE IS DONE: -

    def test_dashboard_displays_all_user_teams(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user_teams = Team.objects.filter(members=self.user) 
        for team in user_teams:
            self.assertContains(response, team.title)
    '''
