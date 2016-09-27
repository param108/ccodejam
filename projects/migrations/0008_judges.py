# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-09-26 21:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_scoreqn_subqn'),
    ]

    operations = [
        migrations.CreateModel(
            name='Judges',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Batch')),
            ],
        ),
    ]