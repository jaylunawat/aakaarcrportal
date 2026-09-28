from django.db import models
# Import the built-in User model from Django for authentication
from django.contrib.auth.models import User 

# This model appears to be your user profile. Let's keep it for now.
# It's better to link this to Django's User model with a OneToOneField
# but we can address that later.
class TaskZero(models.Model):
    crid = models.CharField(max_length=10)
    names = models.CharField(max_length = 200)
    username = models.CharField(max_length = 200)
    email = models.CharField(max_length = 200)
    emails = models.CharField(max_length = 200)
    colgName = models.CharField(max_length = 200)
    state = models.CharField(max_length = 200)
    city = models.CharField(max_length=200, default='')
    mobileNo = models.CharField(max_length=10)
    dept = models.CharField(max_length = 200)
    whatsappNo = models.CharField(max_length = 10)
    pincode = models.CharField(max_length = 6)
    address = models.CharField(max_length = 200)
    
    def __str__(self):
        return f"{self.username} | {self.crid}"

# --- NEW AND IMPROVED MODELS ---

# 1. This model defines what a task is.

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    points = models.IntegerField(default=100)
    # This is the new field for the deadline
    deadline = models.DateTimeField(null=True, blank=True, help_text="Optional: The task will disappear after this date.")

    def __str__(self):
        return self.title

    def __str__(self):
        return self.title

# 2. This model stores a user's submission for a specific task.
class Submission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.URLField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.IntegerField(default=0)
    # This new field will track if you have graded the submission
    graded = models.BooleanField(default=False)

    def __str__(self):
        return f"Submission by {self.user.username} for {self.task.title}"

# We are removing all the old, repetitive models like taskOne, taskTwo, etc.
# The email_auto model seems unused for the task system, so I've removed it for clarity.
# If you use it elsewhere, you can add it back in.