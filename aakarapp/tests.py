from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .admin import SubmissionAdminForm
from .models import Submission, Task


class AdminOperationsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="operations",
            email="operations@example.com",
            password="temporary-test-password",
        )
        self.participant = User.objects.create_user(
            username="participant",
            email="participant@example.com",
        )
        self.task = Task.objects.create(
            title="Campus outreach",
            description="Document the outreach activity.",
            points=100,
        )
        self.submission = Submission.objects.create(
            task=self.task,
            user=self.participant,
            link="https://example.com/proof",
        )
        self.client.force_login(self.admin)

    def test_admin_dashboard_prioritises_review_workflow(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Manage tasks, reviews and points.")
        self.assertContains(response, "Review pending submissions")
        self.assertContains(response, "Awaiting review")

    def test_submission_queue_renders_scoring_controls(self):
        response = self.client.get(reverse("admin:aakarapp_submission_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Open link")
        self.assertContains(response, "Pending")
        self.assertContains(response, "Maximum")

    def test_submission_form_rejects_score_above_task_maximum(self):
        form = SubmissionAdminForm(
            data={
                "task": self.task.pk,
                "user": self.participant.pk,
                "link": "https://example.com/proof",
                "marks": 101,
                "graded": True,
            },
            instance=self.submission,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("worth 100 points", form.errors["marks"][0])

    def test_full_points_action_updates_score_and_review_state(self):
        response = self.client.post(
            reverse("admin:aakarapp_submission_changelist"),
            {
                "action": "award_full_points",
                "_selected_action": [self.submission.pk],
                "index": 0,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.marks, 100)
        self.assertTrue(self.submission.graded)
