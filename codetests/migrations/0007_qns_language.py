# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-03 03:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codetests', '0006_auto_20160731_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='qns',
            name='language',
            field=models.CharField(choices=[('any', 'any'), ('C', 'C'), ('Python', 'Python')], default='any', max_length=20),
        ),
    ]
