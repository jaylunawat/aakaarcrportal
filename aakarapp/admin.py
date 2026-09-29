from django import forms
from django.contrib import admin, messages
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import Submission, Task, TaskZero


admin.site.site_header = "Aakaar CR operations"
admin.site.site_title = "Aakaar CR operations"
admin.site.index_title = "Programme control room"


class SubmissionAdminForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = "__all__"

    def clean_marks(self):
        marks = self.cleaned_data.get("marks")
        task = self.cleaned_data.get("task") or getattr(self.instance, "task", None)

        if marks is None:
            return marks
        if marks < 0:
            raise forms.ValidationError("Points cannot be negative.")
        if task and marks > task.points:
            raise forms.ValidationError(
                f"This task is worth {task.points} points. Enter a score from 0 to {task.points}."
            )
        return marks


@admin.register(TaskZero)
class TaskZeroAdmin(ImportExportModelAdmin):
    list_display = (
        "names",
        "crid",
        "username",
        "email",
        "mobileNo",
        "colgName",
        "city",
    )
    search_fields = ("names", "username", "crid", "email", "mobileNo", "colgName")
    list_filter = ("state", "city", "colgName")
    list_per_page = 40
    ordering = ("names",)


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = (
        "title",
        "points",
        "deadline",
        "task_status",
        "submission_count",
        "pending_count",
    )
    search_fields = ("title", "description")
    list_filter = ("deadline",)
    date_hierarchy = "deadline"
    ordering = ("-deadline", "title")
    list_per_page = 30

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _submission_count=Count("submission", distinct=True),
            _pending_count=Count(
                "submission",
                filter=Q(submission__graded=False),
                distinct=True,
            ),
        )

    @admin.display(description="Status")
    def task_status(self, obj):
        if obj.deadline and obj.deadline < timezone.now():
            return format_html('<span class="status-pill status-closed">Closed</span>')
        return format_html('<span class="status-pill status-live">Live</span>')

    @admin.display(description="Submissions", ordering="_submission_count")
    def submission_count(self, obj):
        return obj._submission_count

    @admin.display(description="Awaiting review", ordering="_pending_count")
    def pending_count(self, obj):
        if obj._pending_count:
            return format_html('<strong class="pending-number">{}</strong>', obj._pending_count)
        return "0"


@admin.register(Submission)
class SubmissionAdmin(ImportExportModelAdmin):
    form = SubmissionAdminForm
    list_display = (
        "participant",
        "task",
        "submitted_at",
        "submission_evidence",
        "marks",
        "available_points",
        "graded",
        "grading_status",
    )
    list_filter = ("graded", "task", "submitted_at")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "task__title",
    )
    list_editable = ("marks", "graded")
    list_select_related = ("task", "user")
    list_per_page = 40
    date_hierarchy = "submitted_at"
    ordering = ("graded", "-submitted_at")
    readonly_fields = ("submitted_at", "submission_evidence")
    actions = ("award_full_points", "mark_as_reviewed", "return_to_pending")
    fieldsets = (
        (
            "Submission",
            {
                "fields": ("task", "user", "submitted_at", "link", "file", "submission_evidence"),
                "description": "Open the submitted evidence before assigning points.",
            },
        ),
        (
            "Review",
            {
                "fields": ("marks", "graded"),
                "description": "Enter a score up to the task maximum, then mark the submission as reviewed.",
            },
        ),
    )

    @admin.display(description="Participant", ordering="user__username")
    def participant(self, obj):
        full_name = obj.user.get_full_name().strip()
        return full_name or obj.user.username

    @admin.display(description="Evidence")
    def submission_evidence(self, obj):
        if obj.file:
            return format_html(
                '<a class="evidence-link" href="{}" target="_blank" rel="noopener">Open file <span aria-hidden="true">↗</span></a>',
                obj.file.url,
            )
        if obj.link:
            return format_html(
                '<a class="evidence-link" href="{}" target="_blank" rel="noopener">Open link <span aria-hidden="true">↗</span></a>',
                obj.link,
            )
        return format_html('<span class="evidence-missing">No evidence</span>')

    @admin.display(description="Maximum", ordering="task__points")
    def available_points(self, obj):
        return f"/ {obj.task.points}"

    @admin.display(description="Review state", ordering="graded")
    def grading_status(self, obj):
        if obj.graded:
            return format_html('<span class="status-pill status-reviewed">Reviewed</span>')
        return format_html('<span class="status-pill status-pending">Pending</span>')

    @admin.action(description="Award full task points and mark as reviewed")
    def award_full_points(self, request, queryset):
        updated = 0
        for submission in queryset.select_related("task"):
            submission.marks = submission.task.points
            submission.graded = True
            submission.save(update_fields=("marks", "graded"))
            updated += 1
        self.message_user(
            request,
            f"Awarded full points to {updated} submission{'s' if updated != 1 else ''}.",
            messages.SUCCESS,
        )

    @admin.action(description="Mark selected submissions as reviewed")
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.update(graded=True)
        self.message_user(request, f"Marked {updated} submission(s) as reviewed.", messages.SUCCESS)

    @admin.action(description="Return selected submissions to pending review")
    def return_to_pending(self, request, queryset):
        updated = queryset.update(graded=False)
        self.message_user(request, f"Returned {updated} submission(s) to the review queue.", messages.WARNING)
