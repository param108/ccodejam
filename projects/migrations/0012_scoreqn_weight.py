# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-29 17:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_scoreans_scorecarduser'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoreqn',
            name='weight',
            field=models.IntegerField(default=1),
        ),
    ]