# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-30 12:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codetests', '0004_auto_20160730_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qns',
            name='largescore',
            field=models.IntegerField(default=5, null=True),
        ),
    ]