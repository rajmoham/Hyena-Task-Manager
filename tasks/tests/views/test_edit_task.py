from django.test import TestCase
from django.urls import reverse
from tasks.models import Task, User, Team


class NewTaskTest(TestCase):


    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_users.json',
        'tasks/tests/fixtures/default_task.json'
        ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username = "@johndoe")
        self.team = Team.objects.get(pk=1)
        self.team.members.add(self.user)
        self.task = Task.objects.get(pk=1)
        self.url = reverse('edit_task', kwargs={'task_id': self.team.id})
        self.data = {'title': 'New Task','description': 'The quick brown fox jumps over the lazy dog.', "due_date": "2040-02-01T12:00:00Z"}

    def test_edit_task_url(self): 
        self.assertEqual(self.url,'/edit_task/' + str(self.task.id))

    def test_get_edit_task_is_allowed(self):
        self.client.login(username=self.user.username, password="Password123")
        task_count_before = Task.objects.count()
        response = self.client.get(self.url, follow=True)
        task_count_after = Task.objects.count()
        self.assertEqual(task_count_after, task_count_before)
        self.assertEqual(response.status_code, 200)

    def test_successful_edit_task(self):
        self.client.login(username=self.user.username, password="Password123")
        user_count_before = Task.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Task.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        new_task = Task.objects.latest('created_at')
        response_url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_team.html')

    def test_unsuccessful_edit_task_from_user_not_in_team(self):
        self.client.login(username='@janedoe', password='Password123')
        user_count_before = Task.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Task.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_sucessful_task_edit_redirects_to_team_page(self):
        self.client.login(username=self.user.username, password="Password123")
        task_count_before = Task.objects.count()
        response = self.client.post(self.url, self.data,follow=True)
        redirect_url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_team.html')
        task_count_after = Task.objects.count()
        self.assertEqual(task_count_after, task_count_before)
        self.assertEqual(response.status_code, 200)
    
    #TODO: Make Tests More Complete