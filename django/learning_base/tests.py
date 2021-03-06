from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User, Group, UserManager

from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from rest_framework.exceptions import ParseError

from learning_base import views, models, serializers
from learning_base.models import Profile
import learning_base.multiple_choice as MultipleChoice
import learning_base.info as InformationText


class DatabaseMixin():
    def setup_database(self):
        self.factory = APIRequestFactory()

        self.admin_group = Group.objects.create(name='admin')
        self.mod_group = Group.objects.create(name='moderator')

        self.u1 = User(username='admin')
        self.u1.save()
        self.u1.groups.add(self.admin_group)
        self.u1_profile = Profile.objects.create(user=self.u1)
        self.u1.save()

        self.normal_user = User.objects.create(username='normal user')
        self.normal_user.profile = Profile.objects.create(
            user=self.normal_user)

        self.moderator = User.objects.create(username='moderator')
        self.moderator.groups.add(self.mod_group)
        self.moderator.profile = Profile.objects.create(user=self.moderator)
        self.moderator.save()

        self.category = models.CourseCategory(name='test')
        self.category.save()

        self.c1_test_en = models.Course(name='test_1', category=self.category,
                                        difficulty=0, language='en',
                                        responsible_mod=self.u1,
                                        is_visible=True)
        self.c1_test_en.save()

        self.m1_test = models.Module(name='module_1', course=self.c1_test_en,
                                     order=1)
        self.m1_test.save()

        self.q1_test = MultipleChoice.models.MultipleChoiceQuestion(
            title='',
            text='a question',
            feedback='',
            order=1,
            module=self.m1_test)
        self.q1_test.save()

        self.a1_test = MultipleChoice.models.MultipleChoiceAnswer(
            question=self.q1_test,
            text='something',
            is_correct=False
        )
        self.a1_test.save()

        self.a2_test = MultipleChoice.models.MultipleChoiceAnswer(
            question=self.q1_test,
            text='something',
            is_correct=True)
        self.a2_test.save()

        self.q2_test = InformationText.models.InformationText(
            title='',
            text='an information text',
            feedback='',
            order=2,
            module=self.m1_test)
        self.q2_test.save()

        self.q3_test = InformationText.models.InformationYoutube(
            title='youtube video',
            text='an information text',
            url='',
            feedback='',
            order=3,
            module=self.m1_test)
        self.q3_test.save()


class AnswerViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.view = views.AnswerView.as_view()
        self.setup_database()

    def test_get(self):
        request = self.factory.get('/courses/1/1/1/answers')
        force_authenticate(request, self.u1)
        response = self.view(request, 1, 0, 0)

        answer_1_serialized = serializers.get_answer_serializer(self.a1_test)
        answer_2_serialized = serializers.get_answer_serializer(self.a2_test)

        self.assertEqual(response.data,
                         [answer_1_serialized, answer_2_serialized])


class MultiCourseViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.MultiCourseView.as_view()

        self.setup_database()

    def test_get(self):
        request = self.factory.get('/courses/')
        force_authenticate(request, self.u1)
        response = self.view(request)
        self.assertEqual(response.status_code, 405)

    def test_post(self):
        request_1 = self.factory.post('/courses/', {'type': '',
                                                    'language': 'de',
                                                    'category': ''})
        request_1.user = self.u1

        request_2 = self.factory.post('/courses/', {'type': '',
                                                    'language': 'en',
                                                    'category': ''})
        request_3 = self.factory.post('/courses/',
                                      {'stuff': 'kajiger'})

        force_authenticate(request_1, self.u1)
        force_authenticate(request_2, self.u1)
        force_authenticate(request_3, self.u1)

        c1_test_en_serialized = serializers.CourseSerializer(
            self.c1_test_en, context={'request': request_1}).data

        response_1 = self.view(request_1)
        response_2 = self.view(request_2)
        response_3 = self.view(request_3)

        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_1.data, [])

        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_2.data, [c1_test_en_serialized])

        self.assertEqual(response_3.status_code, 400)


class CourseViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.CourseView.as_view()

        self.setup_database()

    def test_get(self):
        request = self.factory.get('/courses/1')
        request.user = self.u1
        force_authenticate(request, self.u1)

        c1_test_en_serialized = serializers.CourseSerializer(
            self.c1_test_en, context={'request': request}).data

        response = self.view(request, course_id=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, c1_test_en_serialized)

    def test_post(self):
        request = self.factory.post('/courses/save',
                                    {'name': 'test_2',
                                     'category': 'test',
                                     'difficulty': 2,
                                     'modules': [{'name': 'a module',
                                                  'learning_text': 'no way',
                                                  'order': 3,
                                                  'questions': [
                                                      {'title': 'a question',
                                                       'text': 'some text',
                                                       'feedback': '',
                                                       'type': 'multiple_choice',
                                                       'order': 1,
                                                       'answers': [
                                                           {'text': 'nope',
                                                            'is_correct': True},
                                                           {'text': 'nope',
                                                            'is_correct': False}]}]}],
                                     'language': 'en'}, format='json')
        force_authenticate(request, self.u1)
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.Course.objects.filter(name='test_2').exists())

        request = self.factory.post('/courses/save',
                                    {'name': 'test_2',
                                     'category': 'test',
                                     'difficulty': 2,
                                     'modules': [{'name': 'a module',
                                                  'learning_text': 'no way',
                                                  'order': 3,
                                                  'questions': [
                                                      {'title': 'a question',
                                                       'text': 'some text',
                                                       'feedback': '',
                                                       'type': 'MultipleChoiceQuestion',
                                                       'order': 1,
                                                       'answers': [
                                                           {'text': 'nope',
                                                            'is_correct': False}]}]}],
                                     'language': 'en'}, format='json')
        force_authenticate(request, self.u1)
        response = self.view(request)
        self.assertEqual(response.status_code, 409)

        request = self.factory.post('/courses/save',
                                    {'name': 'test_3',
                                     'category': 'test',
                                     'difficulty': 2,
                                     'modules': [
                                         {'name': 'a module',
                                          'learning_text': 'no way',
                                          'order': 3,
                                          'questions': [
                                              {'title': 'a question',
                                               'text': 'some text',
                                               'feedback': '',
                                               'type': 'multiple_choice',
                                               'order': 1,
                                               'answers': [
                                                   {'text': 'nope',
                                                    'is_correct': True}]
                                               }]},
                                         {'name': 'another module',
                                          'learning_text': 'appearing first',
                                          'order': 2,
                                          'questions': [
                                              {'title': 'a question',
                                               'text': 'some text',
                                               'feedback': '',
                                               'type': 'multiple_choice',
                                               'order': 1,
                                               'answers': [
                                                   {'text': 'nope',
                                                    'is_correct': True}]
                                               }]}],
                                     'language': 'en'}, format='json')
        force_authenticate(request, self.u1)
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.Course.objects.filter(name='test_3').exists())
        self.assertTrue(models.Module.objects.filter(name='a module').exists())
        self.assertTrue(
            models.Module.objects.filter(name='another module').exists())

        request = self.factory.post('/courses/save',
                                    {'name': 'test_4',
                                     'category': 'test',
                                     'difficulty': 2,
                                     'modules': [{'name': 'any module',
                                                  'learning_text': 'no way',
                                                  'order': 0,
                                                  'questions': [
                                                      {
                                                          'title': 'some question',
                                                          'text': 'any text',
                                                          'feedback': '',
                                                          'type': 'multiple_choice',
                                                          'order': 1,
                                                          'answers': [
                                                              {
                                                                  'text': 'this is not correct',
                                                                  'is_correct': False}]}]}],
                                     'language': 'en'}, format='json')
        force_authenticate(request, self.u1)
        response = self.view(request)
        self.assertEquals(response.status_code, 400)
        self.assertFalse(models.Course.objects.filter(name='test_4').exists())
        self.assertFalse(
            MultipleChoice.models.MultipleChoiceQuestion.objects.filter(
                title='any module').exists())

        request = self.factory.post('/courses/save',
                                    {'name': 'test_4',
                                     'category': 'test',
                                     'difficulty': 2,
                                     'modules': [
                                         {'name': 'a module',
                                          'learning_text': 'no way',
                                          'order': 3,
                                          'questions': [
                                              {'title': 'a question',
                                               'text': 'some text',
                                               'feedback': '',
                                               'type': 'multiple_choice',
                                               'order': 1,
                                               'answers': [
                                                   {'text': 'nope',
                                                    'is_correct': True}]
                                               }]}],
                                     'language': 'en'}, format='json')
        force_authenticate(request, self.u1)
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.Course.objects.filter(name='test_4').exists())
        self.assertTrue(
            MultipleChoice.models.MultipleChoiceQuestion.objects.filter(
                title='a question').exists())

    def test_information_text(self):
        request = self.factory.post('/courses/save',
                                    {'name': 'test_4',
                                     'category': 'test',
                                     'difficulty': 2,
                                     'modules': [
                                         {'name': 'a module',
                                          'learning_text': 'no way',
                                          'order': 3,
                                          'questions': [
                                              {'title': 'a question',
                                               'text': 'some text',
                                               'feedback': '',
                                               'type': 'info_text',
                                               'order': 1,
                                               }]}],
                                     'language': 'en'}, format='json')
        force_authenticate(request, self.u1)
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.Course.objects.filter(name='test_4').exists())
        self.assertTrue(
            InformationText.models.InformationText.objects.filter(
                title='a question').exists())


class CourseEditViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.CourseView.as_view()

        self.setup_database()

    def test_deleting_question(self):
        courseData = {
            'name': 'edit_1',
            'category': 'test',
            'difficulty': 2,
            'responsible_mod': 1,
            'responsible_mod': self.u1,
            'modules': [
                {
                    'name': 'a module',
                    'learning_text': 'no way',
                    'order': 3,
                    'questions': [
                        {
                            'title': 'a question',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 1,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        },
                        {
                            'title': 'this one will be removed',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 2,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        }
                    ]
                }
            ],
            'language': 'en'}

        course = serializers.CourseSerializer(data=courseData)
        if not course.is_valid():
            self.assertTrue(False)
        course.create(courseData)
        self.assertTrue(models.Course.objects.filter(name='edit_1').exists())

        request = self.factory.get('/courses/')
        request.user = self.u1
        edit = serializers.CourseEditSerializer(
            models.Course.objects.filter(name='edit_1').first()).data

        del edit['modules'][0]['questions'][1]

        import json
        data = json.loads(json.dumps(edit))

        data['modules'][0]['questions'][0]['answers'] = \
            data['modules'][0]['questions'][0]['question_body']['answers']

        del data['modules'][0]['questions'][0]['question_body']

        data['modules'][0]['questions'][0]['order'] = 0

        data['responsible_mod'] = self.u1
        course = serializers.CourseSerializer(data=data)
        if not course.is_valid():
            self.assertTrue(False)
        course.create(data)

        self.assertFalse(models.Question.objects.filter(
            title='this one will be removed').exists())

    def test_deleting_module(self):
        courseData = {
            'name': 'edit_2',
            'category': 'test',
            'difficulty': 2,
            'responsible_mod': 1,
            'responsible_mod': self.u1,
            'modules': [
                {
                    'name': 'a module',
                    'learning_text': 'no way',
                    'order': 3,
                    'questions': [
                        {
                            'title': 'a question',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 1,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        },
                    ]
                },
                {
                    'name': 'another module',
                    'learning_text': 'no way',
                    'order': 4,
                    'questions': [
                        {
                            'title': 'a question',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 1,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        },
                    ]
                }
            ],
            'language': 'en'}

        course = serializers.CourseSerializer(data=courseData)
        if not course.is_valid():
            self.assertTrue(False)
        course.create(courseData)
        self.assertTrue(models.Course.objects.filter(name='edit_2').exists())

        request = self.factory.get('/courses/')
        request.user = self.u1
        edit = serializers.CourseEditSerializer(
            models.Course.objects.filter(name='edit_2').first()).data

        del edit['modules'][1]

        import json
        data = json.loads(json.dumps(edit))

        data['modules'][0]['questions'][0]['answers'] = \
            data['modules'][0]['questions'][0]['question_body']['answers']

        del data['modules'][0]['questions'][0]['question_body']

        data['modules'][0]['questions'][0]['order'] = 0

        data['responsible_mod'] = self.u1
        course = serializers.CourseSerializer(data=data)
        if not course.is_valid():
            self.assertTrue(False)
        course.create(data)

        self.assertFalse(
            models.Module.objects.filter(name='another module').exists())


class ToggleCourseVisibilityViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        # important for this test:
        # c1_test_en and dependent
        self.setup_database()
        self.view = views.ToggleCourseVisibilityView.as_view()

    def test_post(self):
        self.c1_test_en.is_visible = False
        self.c1_test_en.save()
        self.assertFalse(
            models.Course.objects.get(id=self.c1_test_en.id).is_visible
        )
        post_url = "courses/" + str(self.c1_test_en.id) + "/toggleVisibility/"

        request = self.factory.post(
            post_url,
            {"is_visible": "true"},
        )
        force_authenticate(request, self.u1)
        response = self.view(request, self.c1_test_en.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            models.Course.objects.get(id=self.c1_test_en.id).is_visible)

        request = self.factory.post(
            post_url,
            {"is_visible": "false"}
        )
        force_authenticate(request, self.u1)
        response = self.view(request, self.c1_test_en.id)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            models.Course.objects.get(id=self.c1_test_en.id).is_visible)

        # as asserted the current visibility of the test course is false
        request = self.factory.post(post_url)
        force_authenticate(request, self.u1)
        response = self.view(request, self.c1_test_en.id)
        # so now it should be true
        self.assertTrue(
            models.Course.objects.get(id=self.c1_test_en.id).is_visible)
        self.assertEqual(response.status_code, 200)

        # as asserted the current visibility of the test course is true
        request = self.factory.post(post_url)
        force_authenticate(request, self.u1)
        response = self.view(request, self.c1_test_en.id)
        # so now it should be false
        self.assertFalse(
            models.Course.objects.get(id=self.c1_test_en.id).is_visible)
        self.assertEqual(response.status_code, 200)

        # current visibility is False so a not authorized user
        # shouldn't be able to change it
        request = self.factory.post(post_url)
        force_authenticate(request, self.normal_user)
        response = self.view(request, self.c1_test_en.id)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            models.Course.objects.get(id=self.c1_test_en.id).is_visible
        )


class RequestViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.RequestView.as_view()

        self.mod_group = Group(name='moderator')
        self.mod_group.save()

        self.u1 = User(username='user1')
        self.u1.save()
        self.u1_profile = models.Profile(user=self.u1)
        self.u1_profile.save()
        self.u2 = User.objects.create(username='mod')
        self.u2.groups.add(self.mod_group)
        self.u2.save()
        self.u2_profile = models.Profile(user=self.u2)
        self.u2_profile.save()
        self.u3 = User.objects.create(username='spamer')
        self.u3.save()
        self.u3_profile = models.Profile(user=self.u3)
        self.u3_profile.save()
        self.u3.profile.last_modrequest = timezone.now()

        Group(name='admin').save()

    def test_get(self):
        # Test for true positive
        request_1 = self.factory.get('/user/can_request_mod')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'allowed': True})

        # Test for true negative
        request_2 = self.factory.get('/user/can_request_mod')
        force_authenticate(request_2, self.u2)
        response = self.view(request_2)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(not response.data)

        # Test for true negative
        request_3 = self.factory.get('/user/can_request_mod')
        force_authenticate(request_3, self.u3)
        response = self.view(request_3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'allowed': False})

    def test_post(self):
        request_1 = self.factory.post('user/request_mod',
                                      {'reason': 'you need me'}, format='json')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'Request': 'ok'})
        self.assertFalse(self.u1.profile.modrequest_allowed())

        request_2 = self.factory.post('user/request_mod',
                                      {'reason': 'you need me'}, format='json')
        force_authenticate(request_2, self.u2)
        response = self.view(request_2)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.mod_group in self.u2.groups.all())

        request_3 = self.factory.post('user/request_mod',
                                      {'reason': 'you need me'}, format='json')
        force_authenticate(request_3, self.u3)
        response = self.view(request_3)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.mod_group in self.u1.groups.all())


class UserRightsViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.UserRightsView.as_view()

        self.mod_group = Group.objects.create(name='moderator')
        self.admin_group = Group.objects.create(name='admin')

        self.u1 = User.objects.create_user(username='user1')
        self.u1_profile = models.Profile.objects.create(user=self.u1)

        self.u2 = User.objects.create_user(username='mod')
        self.u2.groups.add(self.mod_group)
        self.u2.save()
        self.u2_profile = models.Profile.objects.create(user=self.u2)

        self.u3 = User.objects.create_user(username='admin')
        self.u3.groups.add(self.admin_group)
        self.u3.save()
        self.u3_profile = models.Profile.objects.create(user=self.u3)

        self.u4 = User.objects.create_user(username='spamer')
        self.u4_profile = models.Profile.objects.create(user=self.u4)
        self.u4.profile.last_modrequest = timezone.now()

        self.users = [self.u1, self.u2, self.u3, self.u4]
        # bad users are those who aren't allowed to promote users
        self.bad_users = [self.u1, self.u2, self.u4]

    def test_post(self):
        # check if 403 is correctly thrown
        requests = []
        responses = []
        i = 0
        for request_user in self.bad_users:
            requests.append(self.factory.post(
                'user/' + str(self.u1.id) + '/rights',
                {'right': 'admin', 'action': 'promote'},
                format='json')
            )
            force_authenticate(requests[i], request_user)
            responses.append(self.view(requests[i]))
            self.assertEqual(responses[i].status_code, 403)
            self.assertFalse(self.u1.profile.is_admin())
            i += 1

        # try withdrawing admin rights from every kind of user as an admin
        # it should always work and the user to demote should not be
        # in the admin group afterwards
        for user_to_change in self.users:
            # try withdrawing modrights
            request2 = (self.factory.post(
                'user/' + str(user_to_change.id) + '/rights/',
                {'right': 'moderator', 'action': 'demote'},
                format='json'
            ))
            force_authenticate(request2, self.u3)
            response2 = (self.view(request2, user_id=user_to_change.id))
            self.assertEqual(response2.status_code, 200)
            self.assertFalse(
                user_to_change.groups.filter(name='moderator').exists()
            )

            # try withdrawing admin rights
            request1 = (self.factory.post(
                'user/' + str(user_to_change.id) + '/rights/',
                {'right': 'admin', 'action': 'demote'},
                format='json'
            ))
            force_authenticate(request1, self.u3)
            response1 = (self.view(request1, user_id=user_to_change.id))
            self.assertEqual(response1.status_code, 200)
            self.assertFalse(
                user_to_change.groups.filter(name='admin').exists()
            )

            # return adminrights to the admin user if they were
            # successfully withdrawn
            if (not self.u3_profile.is_admin()):
                self.u3.groups.add(self.admin_group)

            # try granting modrights
            request3 = (self.factory.post(
                'user/' + str(user_to_change.id) + '/rights/',
                {'right': 'moderator', 'action': 'promote'},
                format='json'
            ))
            force_authenticate(request3, self.u3)
            response3 = (self.view(request3, user_id=user_to_change.id))
            self.assertEqual(response3.status_code, 200)
            self.assertTrue(
                user_to_change.groups.filter(name='moderator').exists()
            )

            # try granting admin rights
            request4 = (self.factory.post(
                'user/' + str(user_to_change.id) + '/rights/',
                {'right': 'admin', 'action': 'promote'},
                format='json'
            ))
            force_authenticate(request4, self.u3)
            response4 = (self.view(request4, user_id=user_to_change.id))
            self.assertEqual(response4.status_code, 200)
            self.assertTrue(
                user_to_change.groups.filter(name='admin').exists()
            )


class TryTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.QuestionView.as_view()
        self.setup_database()

        courseData = {
            'name': 'quiz_1',
            'category': 'test',
            'difficulty': 2,
            'responsible_mod': 1,
            'responsible_mod': self.u1,
            'modules': [
                {
                    'name': 'a module',
                    'learning_text': 'no way',
                    'order': 3,
                    'questions': [
                        {
                            'title': 'a question',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 1,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        },
                    ]
                }
            ],
            'language': 'en'}

        course = serializers.CourseSerializer(data=courseData)
        course.create(courseData)

    def test_check_try(self):
        # creation is possible and quiz query is sorted

        course = models.Course.objects.filter(name='quiz_1')
        self.assertTrue(course.exists())

        course = course.first()
        # create one true
        question = MultipleChoice.models.MultipleChoiceAnswer.objects.filter(
            question__module__course__name='quiz_1', is_correct=True).first()
        correct_answer = self.factory.post(
            'courses/' + str(course.id) + '/0/0/',
            {'answers': [question.id]}, format='json')
        force_authenticate(correct_answer, self.u1)

        response = views.QuestionView.as_view()(correct_answer,
                                                course_id=course.id,
                                                module_id=0, question_id=0)
        # create one false
        question = MultipleChoice.models.MultipleChoiceAnswer.objects.filter(
            question__module__course__name='quiz_1', is_correct=False).first()
        false_answer = self.factory.post(
            'courses/' + str(course.id) + '/0/0/',
            {'answers': [question.id]}, format='json')
        force_authenticate(false_answer, self.u1)

        response = views.QuestionView.as_view()(false_answer,
                                                course_id=course.id,
                                                module_id=0, question_id=0)

        get_statistics = self.factory.get('user/statistics/')
        force_authenticate(get_statistics, self.u1)

        response = views.StatisticsView.as_view()(get_statistics)

        self.assertEqual(len(response.data), 2)

    def test_date(self):
        # initalize the database with 2 trys

        self.test_check_try()
        # check date field
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        end = (now + timedelta(days=+1)).strftime('%Y-%m-%d %H:%M:%S.%f')
        start = (now + timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S.%f')

        get_statistics = self.factory.post('user/statistics/',
                                           {'id': self.u1.id,
                                            'date': {'start': start,
                                                     'end': end}},
                                           format='json')
        force_authenticate(get_statistics, self.u1)

        response = views.StatisticsView.as_view()(get_statistics)
        self.assertEqual(len(response.data), 2)

        # check for to old dates
        end = (now + timedelta(days=-2)).strftime('%Y-%m-%d %H:%M:%S.%f')
        start = (now + timedelta(days=-7)).strftime('%Y-%m-%d %H:%M:%S.%f')

        get_statistics = self.factory.post('user/statistics/',
                                           {'id': self.u1.id,
                                            'date': {'start': start,
                                                     'end': end}},
                                           format='json')
        force_authenticate(get_statistics, self.u1)

        response = views.StatisticsView.as_view()(get_statistics)
        self.assertEqual(len(response.data), 0)


class QuizTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.QuestionView.as_view()
        self.setup_database()

        courseData = {
            'name': 'quiz_1',
            'category': 'test',
            'difficulty': 2,
            'responsible_mod': 1,
            'responsible_mod': self.u1,
            'modules': [
                {
                    'name': 'a module',
                    'learning_text': 'no way',
                    'order': 3,
                    'questions': [
                        {
                            'title': 'a question',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 1,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        },
                    ]
                }
            ],
            'quiz': [
                {
                    'question': 'first',
                    'image': '',
                    'answers': [
                        {
                            'text': 'a sdfa sdfasd fasd fa',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'as dfas dasd asfd adsfa sdf',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdds afadsfadsf adsf ads fa dsf',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'adf asdf asdfasdf',
                            'img': '',
                            'correct': False
                        }
                    ]
                },
                {
                    'question': 'sadfasdfasdfas dasd fasd ',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                },
                {
                    'question': 'sadfasdfasdfas dasd fasd ',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                },
                {
                    'question': 'sadfasdfasdfas dasd fasd ',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                },
                {
                    'question': 'last',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                }
            ],
            'language': 'en'}

        course = serializers.CourseSerializer(data=courseData)
        if not course.is_valid():
            self.assertTrue(False)
        course.create(courseData)

    def test_create_quiz(self):
        # creation is possible and quiz query is sorted

        course = models.Course.objects.filter(name='quiz_1')
        self.assertTrue(course.exists())
        course = course.first()
        self.assertEqual(len(course.quizquestion_set.all()), 5)
        self.assertEqual(course.quizquestion_set.all()[0].question, 'first')
        self.assertEqual(course.quizquestion_set.all()[4].question, 'last')

        # try accesing the quiz before answering the questions is not valid

        request = self.factory.get('courses/' + str(course.id) + '/quiz/',
                                   format='json')
        force_authenticate(request, self.u1)

        response = views.QuizView.as_view()(request, course_id=course.id)

        self.assertEqual(response.status_code, 403)

        # check if return value after every question in course is done is
        # correct
        question = MultipleChoice.models.MultipleChoiceAnswer.objects.filter(
            question__module__course__name='quiz_1', is_correct=True).first()
        correct_answer = self.factory.post(
            'courses/' + str(course.id) + '/0/0/',
            {'answers': [question.id]}, format='json')
        force_authenticate(correct_answer, self.u1)

        response = views.QuestionView.as_view()(correct_answer,
                                                course_id=course.id,
                                                module_id=0, question_id=0)
        self.assertEqual(response.data['next'], 'quiz')

        # send post with false or correct answer will return 200 and send to
        # next quiz question

        answer_correct = []
        i = 0
        for ans in course.quizquestion_set.all():

            answers = []
            for quiz in ans.quizanswer_set.all():
                if i is 1:
                    answers.append({'chosen': not quiz.correct, 'id': quiz.id})
                else:
                    answers.append({'chosen': quiz.correct, 'id': quiz.id})

            answer_correct.append({"answers": answers, 'id': ans.id})
            i += 1

        correct_answer = self.factory.post(
            'courses/' + str(course.id) + '/quiz/',
            {"type": "check_answers", "answers": answer_correct},
            format='json')
        force_authenticate(correct_answer, self.u1)

        response = views.QuizView.as_view()(correct_answer,
                                            course_id=course.id,
                                            )

        # return value of correct answer
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.data[0]['solved'])
        self.assertFalse(response.data[1]['solved'])

        answer_wrong = models.QuizAnswer.objects.filter(
            correct=False,
            quiz=course.quizquestion_set.all()[
                0])
        wrong_answer = self.factory.post(
            'courses/' + str(course.id) + '/quiz/0/',
            {'answers': [(lambda x: x.id)(x) for x in answer_wrong]},
            format='json')
        force_authenticate(wrong_answer, self.u1)

        response = views.QuestionView.as_view()(wrong_answer,
                                                course_id=course.id,
                                                module_id=0, question_id=0)

        # return value of wrong answer
        self.assertEqual(response.status_code, 200)

        # creation for unsolvable quiz resolves in error
        courseData = {
            'name': 'quiz_2',
            'category': 'test',
            'difficulty': 2,
            'responsible_mod': 1,
            'responsible_mod': self.u1,
            'modules': [
                {
                    'name': 'a module',
                    'learning_text': 'no way',
                    'order': 3,
                    'questions': [
                        {
                            'title': 'a question',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 1,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        },
                    ]
                },
                {
                    'name': 'another module',
                    'learning_text': 'no way',
                    'order': 4,
                    'questions': [
                        {
                            'title': 'a question',
                            'text': 'some text',
                            'feedback': '',
                            'type': 'multiple_choice',
                            'order': 1,
                            'answers': [
                                {
                                    'text': 'true',
                                    'is_correct': True
                                },
                                {
                                    'text': 'nope',
                                    'is_correct': False
                                }
                            ]
                        },
                    ]
                }
            ],
            'quiz': [
                {
                    'question': 'first',
                    'image': '', 'answers': [
                    {
                        'text': 'a sdfa sdfasd fasd fa',
                        'img': '',
                        'correct': False
                    },
                    {
                        'text': 'as dfas dasd asfd adsfa sdf',
                        'img': '',
                        'correct': False
                    },
                    {
                        'text': 'asdds afadsfadsf adsf ads fa dsf',
                        'img': '',
                        'correct': False
                    },
                    {
                        'text': 'adf asdf asdfasdf',
                        'img': '', 'correct': False
                    }
                ]
                },
                {
                    'question': 'sadfasdfasdfas dasd fasd ',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                },
                {
                    'question': 'sadfasdfasdfas dasd fasd ',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                },
                {
                    'question': 'sadfasdfasdfas dasd fasd ',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                },
                {
                    'question': 'last',
                    'image': '',
                    'answers': [
                        {
                            'text': 'sadfasdfasdfas dfasdf a',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asd fasdf asdf asd fasd f',
                            'img': '',
                            'correct': True
                        },
                        {
                            'text': 'asdf asdf asdf asdf asd ',
                            'img': '',
                            'correct': False
                        },
                        {
                            'text': 'asdf asdf asd',
                            'img': '',
                            'correct': False
                        }
                    ]
                }
            ],
            'language': 'en'}

        quiz = serializers.CourseSerializer(data=courseData)

        self.assertTrue(quiz.is_valid())
        with self.assertRaises(ParseError):
            quiz.create(courseData)
        self.assertFalse(models.Course.objects.filter(name='quiz_2').exists())


class ProfileTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.setup_database()

    def test_unique_hash(self):
        hash_u1_1 = self.u1_profile.get_hash()
        u2 = User(username='u2')
        u2.save()
        u2_profile = Profile(user=u2)
        u2_profile.save()
        hash_u1_2 = self.u1_profile.get_hash()
        hash_u2_1 = u2_profile.get_hash()

        self.assertTrue(hash_u1_1 == hash_u1_2)
        self.assertFalse(hash_u2_1 == hash_u1_1)

    def test_changed_profile_hash(self):
        hash_u1_1 = self.u1_profile.get_hash()
        self.u1_profile.ranking = 100
        self.u1_profile.save()
        hash_u1_2 = self.u1_profile.get_hash()

        self.assertTrue(hash_u1_1 == hash_u1_2)


class UserViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.setup_database()
        self.view = views.UserView.as_view()
        self.test_user = User.objects.create(username='test_user')
        self.test_user.set_password('12345')
        self.test_user.profile = Profile.objects.create(user=self.test_user)
        self.test_user.save()

    def test_get(self):
        # test if an admin can get any user info
        required_fields = ['first_name', 'last_name', 'username', 'email',
                           'id', 'date_joined',
                           'avatar', 'ranking', 'groups']
        request = self.factory.get('user/' + str(self.normal_user.id))
        force_authenticate(request, self.u1)
        response = self.view(request, user_id=self.u1.id)
        self.assertEqual(response.status_code, 200)
        for field in required_fields:
            self.assertTrue(field in response.data)

        # test if a user can access his own but not other users
        request = self.factory.get('user/current')
        force_authenticate(request, self.normal_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        for field in required_fields:
            self.assertTrue(field in response.data)

        request = self.factory.get('user/' + str(self.u1.id))
        force_authenticate(request, self.normal_user)
        response = self.view(request, user_id=self.u1.id)
        self.assertEqual(response.status_code, 403)

    def test_post(self):
        self.assertTrue(self.test_user.check_password('12345'))
        request = self.factory.post('user/current', {
            'oldpassword': '12345',
            'password': '54321',
            'email': self.test_user.email,
            'first_name': self.test_user.first_name,
            'last_name': self.test_user.last_name,
            'avatar': self.test_user.profile.avatar,
        })
        force_authenticate(request, self.test_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)

        request = self.factory.post('user/current', {
            'oldpassword': '54321',
            'email': self.test_user.email,
            'first_name': 'test first name',
            'last_name': self.test_user.last_name,
            'avatar': self.test_user.profile.avatar,
        })
        force_authenticate(request, self.test_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.get(username=self.test_user.username).first_name,
            'test first name')

        request = self.factory.post('user/current', {
            'oldpassword': '123',
            'email': 'please@dont.de',
            'first_name': 'please',
            'last_name': 'dont',
            'avatar': '...',
        })
        force_authenticate(request, self.test_user)
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        updated_user = User.objects.get(id=self.test_user.id)
        self.assertNotEqual(updated_user.email, 'please@dont.de')
        self.assertFalse(updated_user.first_name == 'please')
        self.assertFalse(updated_user.last_name == 'dont')
        self.assertFalse(updated_user.profile.avatar == '...')


class UserRegisterViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.view = views.UserRegisterView.as_view()
        self.factory = APIRequestFactory()

    def test_post(self):
        request = self.factory.post('register/', {
            'username': 'NotYetExisting',
            'password': '12345',
            'profile': {},
            'groups': {},
        }, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, 201)


class QuestionViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.QuestionView.as_view()

        self.setup_database()

    def test_get(self):
        # Test for true positive
        request_1 = self.factory.get('/course/1/1/1')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1, course_id=1, module_id=0,
                             question_id=0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         serializers.QuestionSerializer(self.q1_test, context={
                             'request': request_1}).data)

        # Test for true negative
        response = self.view(request_1, course_id=1, module_id=0,
                             question_id=128)
        self.assertEqual(response.status_code, 404)

        # Test for outer catch
        response = self.view(request_1, course_id=128, module_id=128,
                             question_id=128)
        self.assertEqual(response.status_code, 404)

        # Test for can't access
        response = self.view(request_1, course_id=1, module_id=0,
                             question_id=1)
        self.assertEqual(response.status_code, 403)

    def test_post(self):
        request_1 = self.factory.post('', {'answers': [0, 1]})
        request_1.user = self.u1
        force_authenticate(request_1, self.u1)
        response = self.view(request_1, course_id=1, module_id=0,
                             question_id=0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'evaluate': False})

        can = views.QuestionView().can_access_question(self.u1, self.q2_test,
                                                       1, 1)
        self.assertFalse(can)

        # Test doesn't work because of weird behavior of testing API
        #
        # request_1 = self.factory.post('', {'answers': [2]})
        # request_1.user = self.u1
        # force_authenticate(request_1, self.u1)
        # response = self.view(request_1, course_id=1, module_id=0,
        #                      question_id=0)

        # can = views.QuestionView().can_access_question(self.u1, self.q2_test)
        # self.assertTrue(can)

    def test_can_access_question(self):
        can = views.QuestionView().can_access_question(self.u1, self.q1_test,
                                                       0, 0)
        self.assertTrue(can)

        can = views.QuestionView().can_access_question(self.u1, self.q2_test,
                                                       2, 1)
        self.assertFalse(can)


class PwResetViewTest(DatabaseMixin, TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = views.PwResetView.as_view()

        self.u1 = User.objects.create_user(
            username='user1', email='user1@email.de', password='12345')
        self.u1_profile = models.Profile(user=self.u1)
        self.u1_profile.save()

    def test_post(self):
        # test if an unknown email address will fail with 404
        request = self.factory.post(
            'pw-reset/', {'email': 'thisDoesDefinitelyNotExist@mail.de'},
            format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, 404)

        # test if a known email will change the password
        request = self.factory.post(
            'pw-reset/', {'email': 'user1@email.de'}
        )
        response = self.view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.u1.email, 'user1@email.de')
        tested = User.objects.get(email='user1@email.de')
        self.assertFalse(tested.check_password('12345'))


class QuestionFunctionTests(TestCase, DatabaseMixin):
    def setUp(self):
        self.setup_database()

    def test_quiz_question(self):
        self.assertEqual(
            MultipleChoice.serializer.MultipleChoiceQuestionEditSerializer,
            self.q1_test.get_edit_serializer())

    def test_question(self):
        self.assertTrue(self.q1_test.is_first_question())
        self.assertFalse(self.q2_test.is_first_question())
        self.assertEquals(1, self.q1_test.get_points())

    def test_info_question(self):
        self.assertEquals(0, self.q2_test.get_points())
        self.assertEquals(0, self.q3_test.get_points())
        self.assertEquals(0, self.q2_test.num_correct_answers())
        self.assertEquals(0, self.q3_test.num_correct_answers())
        self.assertEqual(InformationText.serializer.InformationTextSerializer,
                         self.q2_test.get_serializer())
        self.assertEqual(
            InformationText.serializer.InformationYoutubeSerializer,
            self.q3_test.get_serializer())
        self.assertEqual(InformationText.serializer.InformationTextSerializer,
                         self.q2_test.get_edit_serializer())
        self.assertEqual(
            InformationText.serializer.InformationYoutubeSerializer,
            self.q3_test.get_edit_serializer())

        self.assertFalse(self.q2_test.not_solvable())
        self.assertTrue(self.q2_test.evaluate([]))
        self.assertTrue(self.q3_test.evaluate([]))

    def test_multiple_choice_question(self):
        pass

    def test_module(self):
        self.assertEqual(str(self.m1_test), 'module_1')
        self.assertEqual(self.m1_test.num_of_questions(), 3)
        self.assertFalse(self.m1_test.get_previous_in_order())

    def test_course(self):
        self.assertEqual(str(self.c1_test_en), 'test_1')
        self.assertEqual(self.c1_test_en.num_of_modules(), 1)
        self.assertFalse(models.started_courses(self.u1).exists())


class RankingCalculationTest(TestCase):
    def test_ranking(self):
        ranking = views.calculate_quiz_points
        self.assertEqual(ranking(0, 1, 2), 30)
        self.assertEqual(ranking(0, 0.5, 2), 10)
        self.assertEqual(ranking(0, 0, 2), 0)
        self.assertEqual(ranking(0, 0.8, 2), 20)
        self.assertEqual(ranking(0, 1, 1), 15)
        self.assertEqual(ranking(0, 0, 1), 0)

    def test_diff_ranking(self):
        ranking = views.calculate_quiz_points
        self.assertEqual(ranking(0.4, 1, 2), 20)
        self.assertEqual(ranking(0.4, 0.5, 2), 0)
        self.assertEqual(ranking(0.4, 0, 2), 0)
        self.assertEqual(ranking(0.4, 0.8, 2), 10)
        self.assertEqual(ranking(0.4, 1, 1), 10)
        self.assertEqual(ranking(0.4, 0, 1), 0)


class CourseCategoryTest(TestCase, DatabaseMixin):
    def setUp(self):
        self.view = views.CategoryView.as_view()
        self.setup_database()

    def test_get(self):
        request_1 = self.factory.get('/course_categories')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertEqual(200, response.status_code)
        self.assertEqual([{
            'name': str(self.category),
            'color': '#000000',
            'id': 1
        }], response.data)

    def test_post(self):
        request_1 = self.factory.post(
            '/course_categories',
            {
                'name': 'test_category_2',
                'color': '#010101',
            })
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertTrue(
            models.CourseCategory.objects
            .filter(name='test_category_2').exists()
        )
        request_2 = self.factory.post(
            '/course_categories',
            {
                'delete': 'true',
                'id': '2',
            })
        force_authenticate(request_2, self.u1)
        response = self.view(request_2)
        self.assertFalse(
            models.CourseCategory.objects
            .filter(name='test_category_2').exists()
        )


class MultiUserViewTest(TestCase, DatabaseMixin):
    def setUp(self):
        self.view = views.MultiUserView.as_view()
        self.setup_database()

    def test_get(self):
        request_1 = self.factory.get('/course_categories')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertEqual(200, response.status_code)

    def test_post(self):
        request_1 = self.factory.post('/course_categories')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertEqual(405, response.status_code)


class RankingViewTest(TestCase, DatabaseMixin):
    def setUp(self):
        self.view = views.RankingView.as_view()
        self.setup_database()

    def test_get(self):
        request_1 = self.factory.get('/course_categories')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertEqual(serializers.RankingSerializer(models.Profile.objects.all().reverse()).data, response.data)

    def test_post(self):
        request_1 = self.factory.post('/course_categories')
        force_authenticate(request_1, self.u1)
        response = self.view(request_1)
        self.assertEqual(405, response.status_code)
