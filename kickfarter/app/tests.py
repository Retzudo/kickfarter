"""
Ignore Django's features and assume that the relations
between classed are fine. Only check custom methods.
"""
from django.test import TestCase
import os


class User(TestCase):
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
        self.user.delete()
        self.project.delete()
        os.remove(self.file.name)

    def test_pleding(self):
        from app.exceptions import BackingException
        with self.assertRaises(BackingException) as e:
            # Pledging to their own project
            self.user.pledge(10, self.project)
            self.assertContains(e.msg, 'own projects')

        self.project.status = 3

        with self.assertRaises(BackingException) as e:
            # Pledging on a project that is not active
            self.user.pledge(10, self.project)
            self.assertContains(e.msg, 'active projects')

        self.project.status = 0

        pledge = self.user_two.pledge(10, self.project)
        self.assertEqual(10, pledge.amount)
        self.assertEqual(self.project, pledge.project)
        self.assertEqual(self.user_two, pledge.user)

        self.assertEqual(10, self.project.total_pledged_amount())

        with self.assertRaises(BackingException) as e:
            # Pleding again
            self.user.pledge(10, self.project)
            self.assertContains(e.msg, 'already backed')
