from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Team


class NewTeamTest(TestCase):


    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_users.json'
        ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username = "@johndoe")
        self.team = Team.objects.get(pk=1)
        self.url = reverse('create_team')
        self.data = {'title': 'New Team','description': 'The quick brown fox jumps over the lazy dog.',}

    def test_new_team_url(self):
        self.assertEqual(self.url,'/create_team/')

    def test_get_new_team_is_allowed(self):
        self.client.login(username=self.user.username, password="Password123")
        team_count_before = Team.objects.count()
        response = self.client.get(self.url, follow=True)
        team_count_after = Team.objects.count()
        self.assertEqual(team_count_after, team_count_before)
        self.assertEqual(response.status_code, 200)

    def test_successful_new_team(self):
        self.client.login(username=self.user.username, password="Password123")
        user_count_before = Team.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Team.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_team = Team.objects.latest('created_at')
        self.assertEqual(self.user, new_team.author)
        response_url = reverse('dashboard')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_unsuccessful_new_team(self):
        self.client.login(username='@johndoe', password='Password123')
        user_count_before = Team.objects.count()
        self.data['title'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Team.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'create_team.html')

    def test_cannot_create_team_for_another_user(self):
        self.client.login(username='@johndoe', password='Password123')
        other_user = User.objects.get(username = "@janedoe")
        self.data['author'] = other_user.id
        team_count_before = Team.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        team_count_after = Team.objects.count()
        self.assertEqual(team_count_after, team_count_before+1)
        new_team = Team.objects.latest('created_at')
        self.assertEqual(self.user, new_team.author)

    def test_sucessful_team_creation_redirects_to_dashboard(self):
        self.client.login(username=self.user.username, password="Password123")
        team_count_before = Team.objects.count()
        response = self.client.post(self.url, self.data,follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        team_count_after = Team.objects.count()
        self.assertEqual(team_count_after, team_count_before + 1)
        self.assertEqual(response.status_code, 200)

    def test_invalid_team_user_is_not_logged_in(self):
        team_count_before = Team.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        team_count_after = Team.objects.count()
        self.assertEqual(team_count_after, team_count_before)
        self.assertTemplateUsed(response, 'log_in.html')