# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-02 08:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_base', '0019_auto_20170802_0722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multiplechoiceanswer',
            name='img',
            field=models.CharField(blank=True, max_length=255, verbose_name='The Image for the answer'),
        ),
    ]
