# Generated by Django 3.2.5 on 2021-07-28 15:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cafeteria', '0007_gradelevel_lunchperiod'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gradelevel',
            options={'ordering': ['value'], 'verbose_name_plural': 'Grade Levels'},
        ),
    ]