# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-02-27 09:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='reminders_sent',
            field=models.BooleanField(default=False),
        ),
    ]