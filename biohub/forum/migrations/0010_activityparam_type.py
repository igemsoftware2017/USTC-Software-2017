# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-12 02:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0009_auto_20170812_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityparam',
            name='type',
            field=models.CharField(default='', max_length=20),
        ),
    ]