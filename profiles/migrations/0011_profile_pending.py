# Generated by Django 3.2.5 on 2021-07-22 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0010_rename_status_profile_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pending',
            field=models.BooleanField(default=False),
        ),
    ]
