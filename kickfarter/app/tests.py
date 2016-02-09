from django.test import TestCase


class User(TestCase):
    def setUp(self):
        from app.models import User
        from django.core.files.uploadedfile import SimpleUploadedFile
        from app.models import Project

        self.user = User(email='test@example.com')
        self.user_two = User(email='test2@example.com')
        self.user.save()
        self.user_two.save()

        file = SimpleUploadedFile('testimage.jpg', '')
        self.project = Project(
            description='Description',
            goal=10000,
            created_by=self.user,
            cover_image=file,
        )
        self.project.save()

    def tearDown(self):
        self.user.delete()
        self.project.delete()

    def test_pleding(self):
        from app.exceptions import BackingException
        with self.assertRaises(BackingException):
            # Pledging to their own project
            self.user.pledge(10, self.project)

        pledge = self.user_two.pledge(10, self.project)
        self.assertEqual(10, pledge.amount)
        self.assertEqual(self.project, pledge.project)
        self.assertEqual(self.user_two, pledge.user)

        self.assertEqual(10, self.project.total_pledged_amount())

        with self.assertRaises(BackingException):
            # Pleding again
            self.user.pledge(10, self.project)

