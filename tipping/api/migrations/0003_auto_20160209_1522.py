# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-09 05:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20160207_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='fox_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='round',
            name='status',
            field=models.CharField(choices=[('P', 'Pending'), ('O', 'Ongoing'), ('C', 'Completed')], default='P', max_length=10),
        ),
    ]
