# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-08-02 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coding', '0004_userlock'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLockDelete',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField(unique=True)),
            ],
        ),
    ]