# Generated by Django 5.1.5 on 2025-02-12 02:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=225)),
                ('body', models.TextField()),
                ('reward', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='task',
            name='confirmation_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
