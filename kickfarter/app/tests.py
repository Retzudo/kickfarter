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
        os.remove(self.file.name)

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