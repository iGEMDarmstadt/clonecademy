# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-15 18:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_model', '0002_auto_20170615_1835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='date_registered',
        ),
    ]
