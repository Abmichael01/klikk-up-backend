# Generated by Django 5.1.5 on 2025-04-01 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0004_story_created_at_task_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='estimated_time',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='task',
            name='estimated_time',
            field=models.IntegerField(default=1),
        ),
    ]
