# Generated by Django 5.1 on 2024-08-17 15:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafeteria', '0017_lunchperiod_floating_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance_export_path', models.CharField(blank=True, help_text='File path to which current balance export files should be saved.', max_length=255)),
                ('closed_for_break', models.BooleanField(default=False, help_text='Is the cafeteria closed for a school break or holiday?')),
                ('current_year', models.CharField(help_text='The current school year.', max_length=10)),
                ('debt_limit', models.FloatField(default=0.0, help_text='The debt limit at which point users are prevented from ordering.')),
                ('new_card_fee', models.FloatField(default=0.0, help_text='The fee charged for a new lunch card.')),
                ('order_close_time', models.TimeField(default=datetime.time(8, 15), help_text='The time orders should stop being accepted.')),
                ('order_open_time', models.TimeField(default=datetime.time(0, 0), help_text='The time orders should start being accepted.')),
                ('reports_email', models.CharField(blank=True, help_text='The email addresses, comma seperated, to which system reports should be sent.')),
            ],
            options={
                'verbose_name': 'Site Configuration',
            },
        ),
    ]
