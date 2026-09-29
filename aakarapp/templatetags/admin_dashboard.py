from django import template
from django.db.models import Sum
from django.utils import timezone

from aakarapp.models import Submission, Task, TaskZero


register = template.Library()


@register.simple_tag
def admin_dashboard_stats():
    now = timezone.now()
    active_tasks = Task.objects.filter(deadline__isnull=True).count()
    active_tasks += Task.objects.filter(deadline__gte=now).count()

    return {
        "pending_submissions": Submission.objects.filter(graded=False).count(),
        "reviewed_submissions": Submission.objects.filter(graded=True).count(),
        "active_tasks": active_tasks,
        "participants": TaskZero.objects.count(),
        "points_awarded": Submission.objects.filter(graded=True).aggregate(total=Sum("marks"))["total"] or 0,
    }
