from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html

# Import the correct models from your models.py file
from .models import TaskZero, Task, Submission

# Register the TaskZero (User Profile) model and keep import/export functionality
# Find and replace this class in your aakarapp/admin.py

@admin.register(TaskZero)
class TaskZeroAdmin(ImportExportModelAdmin):
    # 👇 I've added more fields to this line to create more columns
    list_display = ('username', 'crid', 'names', 'email', 'mobileNo', 'city', 'colgName')
    
    # I've also expanded the search to include the new fields
    search_fields = ('username', 'crid', 'names', 'email', 'mobileNo', 'colgName')
    
    # Adding filters makes it easy to find users by location or college
    list_filter = ('city', 'state', 'colgName')

# Register the new Task model
@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    list_display = ('title', 'points')
    search_fields = ('title', 'description')

# Register the new Submission model with a more advanced admin view

# Find and replace the SubmissionAdmin class in aakarapp/admin.py

@admin.register(Submission)
class SubmissionAdmin(ImportExportModelAdmin):
    list_display = ('task', 'user', 'submitted_at', 'view_submission_link', 'marks', 'graded', 'grading_status')
    list_filter = ('task', 'graded', 'user') # Added 'graded' to filters
    search_fields = ('user__username', 'task__title')
    
    # You can now edit both marks and the graded status from the list
    list_editable = ('marks', 'graded')
    
    def view_submission_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.file.url)
        elif obj.link:
            return format_html('<a href="{}" target="_blank">View Link</a>', obj.link)
        return "No submission content"
    view_submission_link.short_description = "Submission Content"

    # This function now checks the 'graded' field instead of the marks
    @admin.display(description='Status')
    def grading_status(self, obj):
        if obj.graded: # <-- This is the logic change
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px; border-radius: 5px;">Graded</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 5px; border-radius: 5px;">Pending Review</span>'
        )