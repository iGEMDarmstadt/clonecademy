# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-17 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_base', '0007_auto_20170717_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.TextField(blank=True, help_text='A short and concise name for the question', null=True, verbose_name='Question title'),
        ),
    ]
