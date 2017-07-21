# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-20 11:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_base', '0008_auto_20170717_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(help_text='A short concise name for the course', max_length=144, verbose_name='Course name'),
        ),
    ]
