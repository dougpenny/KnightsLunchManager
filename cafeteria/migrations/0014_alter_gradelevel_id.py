# Generated by Django 3.2.6 on 2021-08-09 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafeteria', '0013_lunchperiod_teacher_distributes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradelevel',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
