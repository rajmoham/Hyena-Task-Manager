""" Tests of the Show Team view """
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User
from tasks.tests.helpers import reverse_with_next


class ShowTeamViewTestCase(TestCase):
    """ Tests of the Show Team view """

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username="@johndoe")

        # teammate but not current logged in user
        self.teammate_1 = User.objects.get(username="@janedoe")

        # mock team created by user
        self.team = Team.objects.create(
            author=self.user,
            title="TeamA",
            description="This is my team",
        )
        self.team.members.add(self.user, self.teammate_1)

        self.url = reverse('show_team', kwargs={'team_id': self.team.id})

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

    def test_show_team_url(self):
        expectedURL = '/team/' + str(self.team.id)
        self.assertEqual(self.url, expectedURL)

    def test_show_team_displays_team_name(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_team.html')
        self.assertContains(response, self.team.title)

    def test_show_team_displays_description(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_team.html')
        self.assertContains(response, self.team.description)

    def test_show_team_displays_all_members(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_team.html')
        membersInTeam = self.team.members.all() 
        for member in membersInTeam:
            self.assertContains(response, member)

    def test_team_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next("log_in", self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get_show_teamwith_invalid_id(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('show_team', kwargs={'team_id': self.team.id+9999999})
        response = self.client.get(url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
    
