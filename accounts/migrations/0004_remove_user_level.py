# Generated by Django 5.1.5 on 2025-04-01 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_level_user_xp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='level',
        ),
    ]
