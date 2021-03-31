# Generated by Django 3.1.7 on 2021-03-29 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_auto_20201110_0707'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='guardian',
            field=models.ManyToManyField(blank=True, related_name='children', related_query_name='child', to='profiles.Profile'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.SmallIntegerField(choices=[(3, 'Guardian'), (1, 'Staff'), (2, 'Student')], default=2),
        ),
    ]
