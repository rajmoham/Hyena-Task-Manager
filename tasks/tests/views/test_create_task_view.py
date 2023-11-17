from django.test import TestCase
from django.urls import reverse
from tasks.models import Task, User, Team


class NewTaskTest(TestCase):


    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_users.json'
        ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username = "@janedoe")
        self.team = Team.objects.get(pk=1)
        self.url = reverse('create_task', kwargs={'team_id': self.team.id})
        self.data = {'title': 'New Task','description': 'The quick brown fox jumps over the lazy dog.', "due_date": "2040-02-01T12:00:00Z"}

    def test_new_task_url(self): 
        #This should be team
        self.assertEqual(self.url,'/create_task/' + str(self.team.id))

    def test_get_new_task_is_allowed(self):
        self.client.login(username=self.user.username, password="Password123")
        task_count_before = Task.objects.count()
        response = self.client.get(self.url, follow=True)
        task_count_after = Task.objects.count()
        self.assertEqual(task_count_after, task_count_before)
        self.assertEqual(response.status_code, 200)

    def test_successful_new_task(self):
        self.client.login(username=self.user.username, password="Password123")
        user_count_before = Task.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Task.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_task = Task.objects.latest('created_at')
        response_url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_team.html')

    def test_unsuccessful_new_task(self):
        self.client.login(username='@johndoe', password='Password123')
        user_count_before = Task.objects.count()
        self.data['title'] = ""
        response = self.client.post(self.url, self.data, follow=True)
        user_count_after = Task.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'create_task.html')

    def test_sucessful_task_creation_redirects_to_team_page(self):
        self.client.login(username=self.user.username, password="Password123")
        task_count_before = Task.objects.count()
        response = self.client.post(self.url, self.data,follow=True)
        redirect_url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'show_team.html')
        task_count_after = Task.objects.count()
        self.assertEqual(task_count_after, task_count_before + 1)
        self.assertEqual(response.status_code, 200)
    
    #TODO: Make Tests More Complete