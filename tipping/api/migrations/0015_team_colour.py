# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2017-02-25 03:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20160310_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='colour',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
