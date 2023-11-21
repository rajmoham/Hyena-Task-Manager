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
        self.task = Task.objects.get(pk=1)
        self.url = reverse('assign_member_to_task', kwargs={'task_id': self.task.id, 'user_id':self.user.id})


    def test_new_task_url(self): 
        self.assertEqual(self.url,'/assign_member_to_task/' + str(self.task.id) + '/' + str(self.user.id))

    def test_successful_unassignment_to_task(self):
        self.client.login(username=self.user.username, password="Password123")
        membersCountBefore = self.task.assigned_members.count()
        response = self.client.post(self.url, follow=True)
        membersCountAfter = self.task.assigned_members.count()
        self.assertEqual(membersCountAfter, membersCountBefore )
        response_url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'show_team.html')


    def test_unsuccessful_assignment_to_task_invalid_user_not_part_of_team(self):
        self.client.login(username='@petrapickles', password='Password123')
        user_count_before = self.task.assigned_members.count()
        response = self.client.post(self.url,follow=True)
        user_count_after = self.task.assigned_members.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'show_team.html')

    def test_successful_assignment(self):
        #UnAssignment
        self.client.login(username=self.user.username, password="Password123")
        membersCountBefore = self.task.assigned_members.count()
        response = self.client.post(self.url, follow=True)
        membersCountAfter = self.task.assigned_members.count()
        self.assertEqual(membersCountAfter, membersCountBefore)
        #Reassignment
        membersCountBefore = self.task.assigned_members.count()
        response = self.client.post(self.url, follow=True)
        membersCountAfter = self.task.assigned_members.count()
        self.assertEqual(membersCountAfter, membersCountBefore)
        response_url = reverse('show_team', kwargs={'team_id': self.team.id})
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )