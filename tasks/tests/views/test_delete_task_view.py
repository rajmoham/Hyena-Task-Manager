from django.test import TestCase
from django.urls import reverse
from tasks.models import Task, User, Team


class NewTaskTest(TestCase):


    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_teams.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_task.json',
        'tasks/tests/fixtures/other_tasks.json'
        ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username = "@johndoe")
        self.team = Team.objects.get(pk=1)
        self.team.members.add(self.user)
        self.task = Task.objects.get(pk=1)
        self.url = reverse('delete_task', kwargs={'task_id': self.task.id})
        self.data = {'title': 'New Task','description': 'The quick brown fox jumps over the lazy dog.', "due_date": "2040-02-01T12:00:00Z"}


    def test_delete_task_url(self): 
        self.assertEqual(self.url,'/delete_task/' + str(self.task.id))

    def test_successful_delete_task(self):
        self.client.login(username=self.user.username, password="Password123")
        user_count_before = Task.objects.count()
        response = self.client.post(self.url, follow=True)
        user_count_after = Task.objects.count()
        self.assertEqual(user_count_after, user_count_before - 1)
        response_url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_team.html')


    def test_unsuccessful_deletion_task_user_who_is_not_creator_of_team_tries_to_delete_task(self):
        self.client.login(username='@petrapickles', password='Password123')
        user_count_before = Task.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Task.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_unsucessful_deletion_user_who_is_not_part_of_the_team_tries_to_delete_task(self):
        self.client.login(username=self.user.username, password="Password123")
        task_count_before = Task.objects.count()
        # use pk=5 to associate task of another team
        task = Task.objects.get(pk=5)
        team = task.author
        url = reverse('delete_task', kwargs={'task_id': task.id})
        response = self.client.post(url, follow=True)
        #redirect_url = reverse('show_team', kwargs={'team_id': team.id})
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        task_count_after = Task.objects.count()
        self.assertEqual(task_count_after, task_count_before)
        self.assertEqual(response.status_code, 200)

    def test_invalid_deletion_user_is_not_logged_in(self):
        task_count_before = Task.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        task_count_after = Task.objects.count()
        self.assertEqual(task_count_after, task_count_before)
        self.assertTemplateUsed(response, 'log_in.html')