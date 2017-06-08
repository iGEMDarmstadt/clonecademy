from django.db import models
from django.contrib.auth.models import User
from learning_base import models as lb_models
from learning_base.question import models as question_model
from django.core.exceptions import ValidationError
from datetime import datetime
from clonecadamy.settings import FRONT_END_HOSTNAME, PROFILE_PATH


class LearningGroup(models.Model):
    """
    A user group
    """
    name = models.CharField(help_text="The name of the user group", max_length=144)

    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    The profile of a user, storing information about its completed courses etc.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
        #related_name = "profile"
        #could ease access to the corespending profile from a given user
    )
    group = models.OneToOneField(
        LearningGroup,
        null=True,
        on_delete=models.SET_NULL
    )
    date_registered = models.DateField()
    is_mod = models.BooleanField(
        default=False
    )
    is_trusted_mod = models.BooleanField(
        default=False
    )
    requested_mod = models.BooleanField(
        default=False
    )

    def get_link_to_profile(self):
        return FRONT_END_HOSTNAME + PROFILE_PATH + self.user.username

    def __str__(self):
        return self.user.__str__()


class Try(models.Model):
    person = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=False
    )
    question = models.ForeignKey(
        question_model.Question,
        null=True,
        on_delete=models.SET_NULL,
    )
    answer = models.TextField(
        verbose_name="The given answer",
        help_text="The answers as pure string",
        null=True
    )
    date = models.DateTimeField(
        default=datetime.now,
        null=True
    )
    solved = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return "Question: {} was solved {} on {}".format(self.question, self.solved, self.date)


class CourseCompletion(models.Model):
    """
    A field holding reference for a user that completed a course. This makes it possible
    to track, when a user completed the course
    """
    person = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        lb_models.Course,
        on_delete=models.CASCADE
    )
    date = models.DateField()

    def __str__(self):
        return self.name


class Progress(models.Model):
    """
    A field tracking a users progress in different modules.
    """
    person = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        lb_models.Course,
        on_delete=models.CASCADE
    )
    date = models.DateField()

    # question_id = models.ForeignKey(lb_models.Question)

    def clean():
        if (question_id.getCourse != course):
            raise ValidationError(_('Course has no matching question'))

    def __str__(self):
        return self.name
