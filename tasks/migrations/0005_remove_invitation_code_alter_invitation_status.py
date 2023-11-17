# Generated by Django 4.2.6 on 2023-11-16 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_invitation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invitation',
            name='code',
        ),
        migrations.AlterField(
            model_name='invitation',
            name='status',
            field=models.CharField(choices=[('invited', 'Invited'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='invited', max_length=20),
        ),
    ]