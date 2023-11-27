""" Tests of the Show Team view """
from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User, Task
from tasks.tests.helpers import reverse_with_next


class ShowTeamViewTestCase(TestCase):
    """ Tests of the Show Team view """

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

        # we will be viewing the show_team.html of this team
        self.url = reverse('show_team', kwargs={'team_id': self.team.id})

        # other team user does not belong - used to associate other tasks
        self.otherTeam = Team.objects.get(pk=4)

        self.myTeamTask1 = Task.objects.get(pk=1)
        self.myTeamTask2 = Task.objects.get(pk=2)
        self.myTeamTask3 = Task.objects.get(pk=3)
        self.otherTeamTask1 = Task.objects.get(pk=5)
        self.otherTeamTask2 = Task.objects.get(pk=6)

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

    def test_get_show_team_with_invalid_id(self):
        self.client.login(username=self.user.username, password="Password123")
        url = reverse('show_team', kwargs={'team_id': self.team.id+9999999})
        response = self.client.get(url, follow=True)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
    
    def test_show_team_page_displays_all_tasks_details_created_for_current_team(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_team.html')
        createdTeamTasks = [self.myTeamTask1, self.myTeamTask2, self.myTeamTask3]
        for task in createdTeamTasks:
            self.assertContains(response, task.title)

    def test_show_team_page_does_not_display_tasks_details__not_created_for_current_team(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_team.html')
        otherTeamTasks = [self.otherTeamTask1, self.otherTeamTask2]
        for task in otherTeamTasks:
            self.assertNotContains(response, task.title) # given task titles are different
            # self.assertNotContains(response, task.description) if not unique could cause a fail
            # self.assertNotContains(response, task.due_date) if not unique could cause a fail

    # def test_show_team_displays_invite_members_button(self):
    #     self.client.login(username=self.user.username, password="Password123")
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'show_team.html')
    #     self.assertContains(response, '''<a href="{% url 'invite' team_id=team.id %}" class="btn btn-primary mb-3 mt-3">Invite Members</a>''', html=True)

    # def test_show_team_displays_create_tasks_button(self):
    #     self.client.login(username=self.user.username, password="Password123")
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'show_team.html')
    #     self.assertContains(response, '''<a href='{% url "create_task" team.id%}' class="btn btn-primary" style="color: white;">Create Task</a>''', html=True)
        
        

