# Generated by Django 5.1.5 on 2025-06-29 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0021_story_expired_task_expired'),
    ]

    operations = [
        migrations.AlterField(
            model_name='story',
            name='estimated_time',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='task',
            name='estimated_time',
            field=models.IntegerField(default=0),
        ),
    ]
