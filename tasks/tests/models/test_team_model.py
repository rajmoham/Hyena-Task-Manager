from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import User, Team

class TeamTest(TestCase):

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json',
        'tasks/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.team = Team.objects.get(pk=1)
        self.otherUser = User.objects.get(username="@janedoe")

    def test_valid_message(self):
        try:
            self.team.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_author_must_not_be_blank(self):
        self.team.author = None
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_title_must_not_be_blank(self):
        self.team.title = ''
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_title_must_not_be_overlong(self):
        self.team.title = 'x' * 281
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_description_must_not_be_overlong(self):
        self.team.title = 'x' * 10000
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_created_at_is_not_null(self):
        self.assertIsNotNone(self.team.created_at)

    def test_author_must_be_valid_user(self):
        with self.assertRaises(ValueError):
            self.team.author = ''
            self.team.full_clean()

    def test_team_creation_with_assigned_members(self):
        self.team.members.add(self.user, self.otherUser)
        self.assertEqual(self.team.members.count(), 2)
        self.assertIn(self.user, self.team.members.all())
        self.assertIn(self.otherUser, self.team.members.all())
        self.team.full_clean()

    def test_team_creation_without_assigned_members(self):
        self.assertEqual(self.team.members.count(), 0)

    def test_team_creation_with_invalid_assigned_member_raises_validation_error(self):
        with self.assertRaises(ValueError):
            self.team.members.add(self.user, "invalid_user")
