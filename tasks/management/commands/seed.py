from django.core.management.base import BaseCommand, CommandError

from tasks.models import User, Team, Task

import pytz
from faker import Faker
from random import randint, random

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    TEAM_COUNT = 1000
    TASK_COUNT = 2000
    OVERDUE_PROB = 0.05
    MEMBER_PROB = 0.1
    ASSIGN_PROB = 0.1
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_teams()
        self.create_tasks()
        self.add_team_members()
        self.assign_to_task()

    '''Generating Users'''
    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    '''Generating Teams - Fills the Database with Random Teams'''
    def create_teams(self):
        self.generate_random_teams()

    def generate_random_teams(self):
        team_count = Team.objects.count()
        while team_count < self.TEAM_COUNT:
            print(f"Seeding team {team_count}/{self.TEAM_COUNT}", end='\r')
            self.generate_team()
            team_count = Team.objects.count()
        print("Team seeding complete.      ")

    def generate_team(self):
        author = self.get_random_user()
        title = self.faker.first_name() + "'s Team" 
        description = self.faker.text(max_nb_chars=280)
        created_at = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        self.try_create_team({'author': author, 'title': title, 'description': description, 'created_at': created_at})
    
    def get_random_user(self):
        index = randint(0,self.users.count() -1)
        return self.users[index]
    
    def try_create_team(self, data):
        try:
            self.create_team(data)
        except:
            pass

    def create_team(self, data):
        team = Team.objects.create(
            author=data['author'],
            title=data['title'],
            description=data['description'],
            created_at=data['created_at'],
        )
        team.members.add(data['author'])
    
    #Adds Team Members to each randomly created Team
    def add_team_members(self):
        count = 1
        for team in Team.objects.all():
            print(f"Seed members in team {count}/{self.TEAM_COUNT}", end='\r')
            self.add_members_for_team(team)
            count += 1
        print("Member seeding complete.     ")

    def add_members_for_team(self, team):
        for user in self.users:
            if random() < self.MEMBER_PROB:
                team.members.add(user)


    '''Generating Tasks - Fills the Database with Random Tasks'''
    def create_tasks(self):
        self.generate_random_tasks()

    def generate_random_tasks(self):
        task_count = Task.objects.count()
        while task_count < self.TASK_COUNT:
            print(f"Seeding task {task_count}/{self.TASK_COUNT}", end='\r')
            self.generate_task()
            task_count = Task.objects.count()
        print("Task seeding complete.      ")

    def generate_task(self):
        author = self.get_random_team()
        title = self.faker.first_name() + "'s Task" 
        description = self.faker.text(max_nb_chars=280)
        created_at = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        if random() < self.OVERDUE_PROB:
            due_date = self.faker.future_datetime(end_date='+30d', tzinfo=pytz.UTC)
        else:
            due_date = self.faker.past_datetime(start_date='-365d', tzinfo=pytz.UTC)
        self.try_create_task({'author': author, 'title': title, 'description': description, 'created_at': created_at, 'due_date': due_date})
    
    def get_random_team(self):
        index = randint(0, Team.objects.count() -1)
        return Team.objects.all()[index]
    
    def try_create_task(self, data):
        try:
            self.create_task(data)
        except:
            pass

    def create_task(self, data):
        task = Task.objects.create(
            author=data['author'],
            title=data['title'],
            description=data['description'],
            created_at=data['created_at'],
            due_date=data['due_date'],
        )

    def assign_to_task(self):
        count = 1
        for task in Task.objects.all():
            print(f"Seed assigning members to task {count}/{self.TASK_COUNT}", end='\r')
            self.assign_members_to_task(task)
            count += 1
        print("Member Assignment to Tasks seeding complete.     ")

    def assign_members_to_task(self, task):
        for user in self.users:
            tasks_with_user = task.author.members.filter(id=user.id)
            if tasks_with_user.exists() and random() < self.ASSIGN_PROB:
                task.assigned_members.add(user)

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'
