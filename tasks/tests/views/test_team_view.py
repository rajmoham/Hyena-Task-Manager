from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User


class NewTeamTest(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )
        self.url = reverse('create_team')
        self.data = { "title" : "This is my Team" ,'description': 'The quick brown fox jumps over the lazy dog.' }

    def test_new_team_url(self):
        self.assertEqual(self.url,'/create_team')

    def test_team_new_team_redirects_when_not_logged_in(self):
        user_count_before = Team.objects.count()
        redirect_url = reverse('log_in')
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, redirect_url,
            status_code=302, target_status_code=200, fetch_redirect_response=True
        )
        user_count_after = Team.objects.count()
        self.assertEqual(user_count_after, user_count_before)

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
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_cannot_create_team_for_other_user(self):
        self.client.login(username='@johndoe', password='Password123')
        other_user = User.objects.create_user(
            '@janedoe',
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123',
        )
        self.data['author'] = other_user.id
        user_count_before = Team.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Team.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_team = Team.objects.latest('created_at')
        self.assertEqual(self.user, new_team.author)