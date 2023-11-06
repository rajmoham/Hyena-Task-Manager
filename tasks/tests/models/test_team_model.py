from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import User, Team

class TeamTest(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
        )
        self.team = Team(
            author=self.user,
            title="Team Test",
            description = "This is my new Team",
        )

    def test_valid_message(self):
        try:
            self.team.full_clean()
        except ValidationError:
            self.fail("Test message should be valid")

    def test_author_must_not_be_blank(self):
        self.team.author = None
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_text_must_not_be_blank(self):
        self.team.text = ''
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_text_must_not_be_overlong(self):
        self.team.text = 'x' * 281
        with self.assertRaises(ValidationError):
            self.team.full_clean()