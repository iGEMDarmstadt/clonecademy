# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 10:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_base', '0006_auto_20170821_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question',
            field=models.TextField(blank=True, help_text='This field can contain markdown syntax', null=True, verbose_name='Question'),
        ),
    ]
