# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-16 12:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codetests', '0002_auto_20160716_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codetests',
            name='generating',
        ),
        migrations.AddField(
            model_name='codetests',
            name='generationStatus',
            field=models.CharField(default='NOTSTARTED', max_length=20),
        ),
    ]
