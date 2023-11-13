from django.core.exceptions import ValidationError
from django.test import TestCase
from tasks.models import User, Team

class TeamTest(TestCase):

    fixtures = [
        'tasks/tests/fixtures/default_user.json',
        'tasks/tests/fixtures/default_team.json'
    ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.get(username='@johndoe')
        self.team = Team.objects.get(pk=1)

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

    def test_text_must_not_be_overlong(self):
        self.team.title = 'x' * 281
        with self.assertRaises(ValidationError):
            self.team.full_clean()

    def test_created_at_is_not_null(self):
        self.assertIsNotNone(self.team.created_at)

    #def test_author_must_be_valid_user(self):

    #TODO: Test if adding Members Works Correcty
