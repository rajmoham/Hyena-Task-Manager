
# Generated by Django 4.2.6 on 2023-11-19 23:34
# Generated by Django 4.2.6 on 2023-11-23 14:08

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_merge_20231117_1410'),
        ('tasks', '0010_alter_task_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2023, 11, 19, 23, 34, 20, 491782, tzinfo=datetime.timezone.utc))]),
        ),
    ]
