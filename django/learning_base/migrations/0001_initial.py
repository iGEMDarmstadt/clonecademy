# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-17 12:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A short concise name for the course', max_length=144, unique=True, verbose_name='Course name')),
                ('course_difficulty', models.IntegerField(choices=[(0, 'Easy (high school students)'), (1, 'Moderate (college entry)'), (2, 'Difficult (college students'), (3, 'Expert (college graduates)')], default=1, verbose_name='Course difficulty')),
                ('is_visible', models.BooleanField(default=False, verbose_name='Is the course visible')),
            ],
        ),
        migrations.CreateModel(
            name='CourseCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the category (e.g. biochemistry)', max_length=144)),
            ],
        ),
        migrations.CreateModel(
            name='LearningGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the user group', max_length=144)),
            ],
        ),
        migrations.CreateModel(
            name='ModRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='A short concise name for the module', max_length=144, verbose_name='Module name')),
                ('learning_text', models.TextField(help_text='The learning Text for the module', verbose_name='Learning text')),
                ('module_order', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_base.Course')),
            ],
            options={
                'ordering': ['module_order'],
            },
        ),
        migrations.CreateModel(
            name='MultipleChoiceAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='The answers text', verbose_name='Answer text')),
                ('is_correct', models.BooleanField(default=False, verbose_name='is the answer correct?')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_title', models.TextField(help_text='A short and concise name for the question', verbose_name='Question title')),
                ('question_body', models.TextField(help_text='This field can contain markdown syntax', verbose_name='Question text')),
                ('feedback', models.TextField(help_text='The feedback for the user after a sucessful answer', verbose_name='feedback')),
                ('question_order', models.IntegerField()),
            ],
            options={
                'ordering': ['module', 'question_order'],
            },
        ),
        migrations.CreateModel(
            name='Try',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(help_text='The answers as pure string', null=True, verbose_name='The given answer')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('solved', models.BooleanField(default=False)),
                ('person', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MultipleChoiceQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='learning_base.Question')),
            ],
            options={
                'abstract': False,
            },
            bases=('learning_base.question',),
        ),
        migrations.AddField(
            model_name='try',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='learning_base.Question'),
        ),
        migrations.AddField(
            model_name='question',
            name='module',
            field=models.ForeignKey(help_text='The corresponding module for the question', on_delete=django.db.models.deletion.CASCADE, to='learning_base.Module', verbose_name='feedback'),
        ),
        migrations.AddField(
            model_name='question',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_learning_base.question_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learning_base.CourseCategory'),
        ),
        migrations.AddField(
            model_name='course',
            name='responsible_mod',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='question',
            unique_together=set([('module', 'question_order')]),
        ),
        migrations.AddField(
            model_name='multiplechoiceanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='learning_base.MultipleChoiceQuestion'),
        ),
        migrations.AlterUniqueTogether(
            name='module',
            unique_together=set([('module_order', 'course')]),
        ),
    ]
