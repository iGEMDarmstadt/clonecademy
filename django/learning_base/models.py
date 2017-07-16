from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
from django.utils import timezone
from polymorphic.models import PolymorphicModel


# from user_model import models as ub_models


def get_link_to_profile(user):
    '''
    Returns the link to the users profile page
    TODO: Implement correctly
    '''
    return "clonecademy.com/this/users/profile"


def valid_mod_request(user):
    request = ModRequest.objects.filter(user=user)
    return request.exists() \
           and (request.first().date - timezone.localdate()).days < -7


class Profile(models.Model):
    '''
    '''
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
    )

    last_modrequest = models.DateField(
        blank=True,
        null=True,
    )

    def get_age(self):
        today = timezone.today
        return today.year - self.birth_date.year \
               - ((today.month, today.day) <
                  (self.birth_date.month, self.birth_date.day))

    def __str__(self):
        return str(self.user)


class CourseCategory(models.Model):
    """
    The type of a course, meaning the field in which the course belongs, e.g.
    biochemistry, cloning, technical details.
    """
    name = models.CharField(
        help_text="Name of the category (e.g. biochemistry)",
        max_length=144
    )

    def get_courses(self):
        return self.course_set

    def __str__(self):
        return self.name


class Course(models.Model):
    """
    One course is a group of questions which build on each other and should be
    solved together. These questions should have similar topics, difficulty
    and should form a compete unit for learning.
    """
    QUESTION_NAME_LENGTH = 144

    EASY = 0
    MODERATE = 1
    DIFFICULT = 2
    EXPERT = 3
    DIFFICULTY = (
        (EASY, 'Easy (high school students)'),
        (MODERATE, 'Moderate (college entry)'),
        (DIFFICULT, 'Difficult (college students'),
        (EXPERT, 'Expert (college graduates)')
    )

    GER = 'de'
    ENG = 'en'
    LANGUAGES = (
        (GER, 'German/Deutsch'),
        (ENG, 'English')
    )

    name = models.CharField(
        verbose_name='Course name',
        help_text="A short concise name for the course",
        unique=True,
        max_length=144
    )

    category = models.ForeignKey(
        CourseCategory,
        null=True,
        blank=True
    )

    difficulty = models.IntegerField(
        verbose_name='Course difficulty',
        choices=DIFFICULTY,
        default=MODERATE
    )

    language = models.CharField(
        verbose_name='Course Language',
        max_length=2,
        choices=LANGUAGES,
        default=ENG
    )

    responsible_mod = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    is_visible = models.BooleanField(
        verbose_name='Is the course visible',
        default=False
    )

    def __str__(self):
        return self.name

    def num_of_modules(self):
        '''
        Returns the number of modules
        '''
        return len(Module.objects.filter(course=self))


class Module(models.Model):
    """
    A Course is made out of several modules and a module contains the questions
    """

    class Meta():
        unique_together = ['order', 'course']
        ordering = ['order']

    name = models.CharField(
        help_text="A short concise name for the module",
        verbose_name='Module name',
        max_length=144
    )

    learning_text = models.TextField(
        help_text="The learning Text for the module",
        verbose_name="Learning text"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    order = models.IntegerField()

    def __str__(self):
        return self.name

    def num_of_questions(self):
        '''
        Returns the number of questions in the module
        '''
        return len(self.question_set.all())

    def is_last_module(self):
        '''
        Returns True if this is the final module in a course
        '''
        modules = self.course.module_set
        return self == modules.last()


class Question(PolymorphicModel):
    """
    A question is the smallest unit of the learning process. A question has a
    task that can be solved by a user, a correct solution to evaluate the
    answer and a way to provide feedback to the user.
    """

    class Meta():
        unique_together = ['module', 'order']
        ordering = ['module', 'order']

    title = models.TextField(
        verbose_name='Question title',
        help_text="A short and concise name for the question"
    )

    body = models.TextField(
        verbose_name='Question text',
        help_text="This field can contain markdown syntax"
    )

    feedback = models.TextField(
        verbose_name="feedback",
        help_text="The feedback for the user after a sucessful answer",
        blank=True,
        null=True
    )

    order = models.IntegerField()

    module = models.ForeignKey(
        Module,
        verbose_name="Module",
        help_text="The corresponding module for the question",
        on_delete=models.CASCADE
    )

    def feedback_is_set(self):
        return len(feedback) != 0

    def is_last_question(self):
        questions = self.module.question_set
        return self == questions.last()

    def __str__(self):
        return self.title


class LearningGroup(models.Model):
    """
    A user group (currently not used)
    """
    name = models.CharField(
        help_text="The name of the user group",
        max_length=144)

    def __str__(self):
        return self.name


class Try(models.Model):
    '''
    A try represents a submission of an answer. Each time an answer is
    submitted, a Try object is created in the database, detailing answer,
    whether it was answered correctly and the time of the submission.
    '''
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )

    question = models.ForeignKey(
        Question,
        null=True,
        on_delete=models.SET_NULL,
    )

    answer = models.TextField(
        verbose_name="The given answer",
        help_text="The answers as pure string",
        null=True
    )

    date = models.DateTimeField(
        default=timezone.now,
        null=True
    )

    solved = models.BooleanField(
        default=False
    )

    def __unicode__(self):
        return "Solution_{}_{}_{}".format(
            self.question, self.solved, self.date)


class CourseManager(models.Manager):
    def is_started(user):
        courses = models.Course.objects.filter(
            module__question__try__person=user)
        return courses
