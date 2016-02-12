"""
Ignore Django's features and assume that the relations
between classes basically are fine. Only check custom methods.
"""
from django.test import TestCase
import os


class UserTest(TestCase):
    def setUp(self):
        from app.models import User
        from django.core.files.uploadedfile import SimpleUploadedFile
        from app.models import Project

        self.user = User(email='test@example.com')
        self.user_two = User(email='test2@example.com')
        self.user.save()
        self.user_two.save()

        self.file = SimpleUploadedFile('testimage.jpg', '', content_type='image/jpeg')
        self.project = Project(
            description='Description',
            goal=10000,
            created_by=self.user,
            cover_image=self.file,
        )
        self.project.save()

    def tearDown(self):
        from kickfarter import settings
        os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))

    def test_pledging(self):
        from app.exceptions import BackingException
        from app.models import Project

        with self.assertRaises(BackingException) as e:
            # Pledging on a project that is not active
            self.user.pledge(100, self.project)
            self.assertContains(e.msg, 'active projects')

        self.project.status = Project.STATUS_ACTIVE

        with self.assertRaises(BackingException) as e:
            # Pledging to their own project
            self.user.pledge(100, self.project)
            self.assertContains(e.msg, 'own projects')

        pledge = self.user_two.pledge(100, self.project)
        self.assertEqual(100, pledge.amount)
        self.assertEqual(self.project, pledge.project)
        self.assertEqual(self.user_two, pledge.user)

        self.assertEqual(self.user_two.pledged_to.first(), self.project)
        self.assertEqual(self.user_two.pledges.first(), pledge)

        with self.assertRaises(BackingException) as e:
            # Pledging again
            self.user.pledge(100, self.project)
            self.assertContains(e.msg, 'already backed')


class ProjectTest(TestCase):
    def setUp(self):
        from app.models import User

        self.user = User(email='test@example.com')
        self.user_two = User(email='test2@example.com')
        self.user.save()
        self.user_two.save()

    def test_project(self):
        from app.models import Project
        project = Project(title='Test Project', description='Test Project', goal=100, created_by=self.user)
        project.save()

        self.assertNotEqual(Project.STATUS_ACTIVE, project.status)
        self.assertTrue(project.is_draft)
        project.publish()
        self.assertEqual(Project.STATUS_ACTIVE, project.status)
        self.assertFalse(project.is_draft)

        self.user_two.pledge(1, project)

        self.assertEqual(1, project.total_pledged_amount)
        self.assertEqual(1, project.percentage_funded)

    def test_duration(self):
        import datetime
        from app.models import Project
        project = Project(title='Test Project', description='Test Project', goal=100, created_by=self.user)
        project.save()

        # 59 days because a tiny tiny amount of time has already passed between save() and this test
        self.assertEqual((59, 'days'), project.time_remaining())

        # Calculate one day remaining
        one_day_before = project.finished_on - datetime.timedelta(days=1)
        self.assertEqual((1, 'days'), project.time_remaining(relative_to=one_day_before))

        # Calculate two hours remaining
        two_hours_before = project.finished_on - datetime.timedelta(hours=2)
        self.assertEqual((2, 'hours'), project.time_remaining(relative_to=two_hours_before))

        # Calculate less than an hour remaining
        less_than_an_hour_before = project.finished_on - datetime.timedelta(minutes=30)
        self.assertEqual((0, 'hours'), project.time_remaining(relative_to=less_than_an_hour_before))

        # Project overdue
        after = project.finished_on + datetime.timedelta(days=1)
        self.assertEqual((0, 'finished'), project.time_remaining(relative_to=after))
