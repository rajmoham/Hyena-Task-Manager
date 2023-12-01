from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import User, Team ,Task
from django.utils import timezone
from datetime import datetime

class TaskTest(TestCase):

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/default_task.json',
        'tasks/tests/fixtures/other_users.json'

    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.team = Team.objects.get(pk=1)
        self.task = Task.objects.get(pk=1)
        self.otherUser = User.objects.get(username="@janedoe")

    def test_valid_message(self):
        try:
            self.task.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_author_must_not_be_blank(self):
        self.task.author = None
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_title_must_not_be_blank(self):
        self.task.title = ''
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_description_must_not_be_blank(self):
        self.task.description = ''
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_text_must_not_be_overlong(self):
        self.task.title = 'x' * 281
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_created_at_is_not_null(self):
        self.assertIsNotNone(self.task.created_at)

    def test_task_creation_with_invalid_due_date(self): 
        self.task.due_date = datetime.fromisoformat("2004-02-01T12:00:00Z")
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_due_date_must_not_be_blank(self):
        self.task.due_date = ''
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_author_must_be_valid_team(self):
        with self.assertRaises(ValueError):
            self.task.author = ''
            self.task.full_clean()

    def test_task_creation_with_assigned_members(self):
        self.task.assigned_members.add(self.user, self.otherUser)
        self.assertEqual(self.task.assigned_members.count(), 2)
        self.assertIn(self.user, self.task.assigned_members.all())
        self.assertIn(self.otherUser, self.task.assigned_members.all())
        self.task.full_clean()

    def test_task_creation_without_assigned_members(self):
        self.assertEqual(self.task.assigned_members.count(), 0)

    def test_task_creation_with_invalid_assigned_member_raises_validation_error(self):
        with self.assertRaises(ValueError):
            self.task.assigned_members.add(self.user, "invalid_user")

    """ def test_due_date_is_overdue(self):
        self.task.due_date = datetime.fromisoformat("2004-02-01T12:00:00Z")
        self.assertTrue(self.task.is_overdue())
    
    def test_due_date_is_not_overdue(self):
        self.task.due_date = datetime.fromisoformat("3030-02-01T12:00:00Z")
        self.assertFalse(self.task.is_overdue()) """
