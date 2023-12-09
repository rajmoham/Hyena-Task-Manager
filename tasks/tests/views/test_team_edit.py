'''Unit test for Edit Team View'''
from django.test import TestCase
from tasks.models import Team, User
from django.urls import reverse
from tasks.tests.helpers import reverse_with_next

class TeamViewTestCase(TestCase):
    '''Unit test for Edit Team View'''

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_teams.json',
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username="@johndoe")
        self.teammate = User.objects.get(username="@janedoe")
        self.team = Team.objects.get(pk=1)
        self.team.members.add(self.user)
        self.url = reverse('edit_team', kwargs={'team_id': self.team.id})
        self.data = {'title': 'Edit Team','description': 'Edit Description'}

    def test_edit_team_url(self):
        expectedURL = '/team/edit_team/' + str(self.team.id)
        self.assertEquals(self.url, expectedURL)

    def test_get_edit_team_is_allowed_for_team_author(self):
        self.client.login(username=self.user.username, password="Password123")
        team_count_before = Team.objects.count()
        response = self.client.get(self.url, follow=True)
        team_count_after = Team.objects.count()
        self.assertEqual(team_count_after, team_count_before)
        self.assertEqual(response.status_code, 200)

    def test_get_edit_team_is_not_allowed_for_other_members(self):
        self.client.login(username=self.teammate.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_successful_edit_team(self):
        self.client.login(username=self.user.username, password="Password123")
        user_count_before = Team.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Team.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        response_url = reverse('dashboard')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'dashboard.html')

    def test__get_edit_team_redirects_when_user_is_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_post_edit_team_redirects_when_user_is_not_logged_in(self):
        team_count_before = Team.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        team_count_after = Team.objects.count()
        self.assertEqual(team_count_after, team_count_before)
        self.assertTemplateUsed(response, 'log_in.html')