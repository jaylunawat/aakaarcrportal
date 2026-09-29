from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib import messages # <--- CHANGE 1: Import the messages framework

# Import the new, refactored models
from .models import TaskZero, Task, Submission

# --- General Views ---

def home(request):
    """Renders the main landing page."""
    return render(request, "home.html")

# --- User Authentication and Profile ---

def register_cr(request):
    """Handles new user registration."""
    if request.method == "POST":
        full_name = request.POST.get('names')
        # We will use the email as the username for simplicity and to ensure uniqueness
        username = request.POST.get('emails') # <--- CHANGE 2: Use email for username
        password = request.POST.get('password')
        email = request.POST.get('emails')
        colg_name = request.POST.get('colName')
        state = request.POST.get('state')
        # The city field was missing from your original view, I've added it.
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        phone_no = request.POST.get('phoneNo')

        try:
            if User.objects.filter(username=username).exists():
                # We can now just check for the username, as it's the same as the email
                return render(request, 'home.html', {'error': 'A user with this email already exists.'})

            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = full_name
            user.save()

            crid = f"AK{250000 + user.id}"
            TaskZero.objects.create(
                crid=crid, names=full_name, username=username, email=email,
                emails=email, colgName=colg_name, state=state, city=city,
                pincode=pincode, mobileNo=phone_no, whatsappNo=phone_no
            )
            
            # --- CHANGE 3: Add a success message ---
            messages.success(request, 'Registration successful! You can now log in.')
            
            # Redirect to the home page to show the success message and login form
            return redirect('home')

        except IntegrityError:
            return render(request, 'home.html', {'error': 'A database error occurred.'})

    return redirect('home')

def user_login(request):
    """Handles user login."""
    
    # --- NEW: Automatically log out any currently logged-in user ---
    if request.user.is_authenticated:
        logout(request)
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            # --- NEW: Check if the user trying to log in is a superuser ---
            if user.is_superuser:
                # Don't log them into the main site, send them to admin
                messages.info(request, "Superuser login is via the admin panel.")
                return redirect('/admin/')
                
            login(request, user)
            return redirect('dashboard')
        else:
            # Use the messages framework for a cleaner error display
            messages.error(request, 'Invalid email or password.')
            return redirect('home')
    
    return redirect('home')

# (The rest of your views.py file remains the same)
def user_logout(request):
    """Logs the user out."""
    logout(request)
    return redirect('home')

# Find and replace the dashboard function in aakarapp/views.py

@login_required
def dashboard(request):
    """
    Renders the CR dashboard with a rank calculation that is consistent
    with the main leaderboard, including tie-breaking.
    """
    if request.user.is_superuser:
        return redirect('/admin/')
    
    profile = TaskZero.objects.filter(username=request.user.username).first()
    is_filled = profile is not None

    # --- REVISED RANKING LOGIC ---
    
    # 1. Get the current user's score.
    current_user_score_data = Submission.objects.filter(user=request.user).aggregate(
        total_score=Coalesce(Sum('marks'), 0)
    )
    current_user_score = current_user_score_data['total_score']

    # 2. Prepare a query of all users with their scores annotated.
    users_with_scores = User.objects.filter(is_superuser=False, is_active=True).annotate(
        total_score=Coalesce(Sum('submission__marks'), 0)
    )
    
    # 3. Count users with a strictly higher score.
    higher_scorers_count = users_with_scores.filter(total_score__gt=current_user_score).count()

    # 4. Count users with the same score but who registered earlier (lower ID).
    tie_breakers_count = users_with_scores.filter(
        total_score=current_user_score,
        id__lt=request.user.id
    ).count()

    # 5. The final rank is 1 + (people with higher scores) + (people with the same score who are ahead of you).
    current_user_rank = higher_scorers_count + tie_breakers_count + 1

    # --- END OF REVISED LOGIC ---
    
    completed_tasks = Submission.objects.filter(user=request.user).select_related('task').order_by('-submitted_at')

    context = {
        'user': request.user,
        'CRID': getattr(profile, 'crid', None),
        'is_filled': is_filled,
        'current_obj': profile,
        'points': current_user_score,
        'rank': current_user_rank, # Use the new, consistent rank
        'completed_tasks': completed_tasks,
    }
    return render(request, "dashboard.html", context)
@login_required
def updateProfile(request):
    """Handles updating a CR's profile, and blocks superusers."""
    # --- NEW: Prevent superusers from creating a profile ---
    if request.user.is_superuser:
        messages.info(request, "Superuser profiles are managed in the admin panel, not here.")
        return redirect('/admin/')

    if request.method == "POST":
        user = request.user
        profile, created = TaskZero.objects.get_or_create(username=user.username)

        profile.crid = f"AK{230000 + user.id}"
        profile.names = request.POST.get('names', user.first_name)
        profile.email = user.email
        profile.emails = request.POST.get('emails', user.email)
        profile.colgName = request.POST.get('colName', '')
        profile.state = request.POST.get('state', '')
        profile.city = request.POST.get('city', '')
        profile.mobileNo = request.POST.get('phoneNo', '')
        profile.dept = request.POST.get('dept', '')
        profile.whatsappNo = request.POST.get('whatsNo', '')
        profile.pincode = request.POST.get('pin', '')
        profile.address = request.POST.get('address', '')
        selected_avatar = request.POST.get('avatar', '')
        valid_avatars = {value for value, _label in TaskZero.AVATAR_CHOICES}
        if selected_avatar in valid_avatars:
            profile.avatar = selected_avatar
        profile.save()

    return redirect('dashboard')

# Find and replace the tasks_page function in aakarapp/views.py

from django.contrib import messages # Make sure this import is at the top of your file
from django.utils import timezone
from django.db.models import Q


def tasks_page(request):
    """
    Displays active tasks and handles submissions with validation.
    """
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        link = request.POST.get('link', '')
        uploaded_file = request.FILES.get('file')

        # --- NEW: Validation Logic ---
        if not link and not uploaded_file:
            # If both fields are empty, send an error message and redirect
            messages.error(request, 'You must submit a link OR a file.')
            return redirect('tasks_page')
        # --- End of Validation Logic ---

        try:
            task = Task.objects.get(id=task_id)
            
            # Create or update the submission. If a user resubmits, it will be
            # marked as ungraded again for you to review.
            submission, created = Submission.objects.update_or_create(
                user=request.user,
                task=task,
                defaults={'link': link, 'file': uploaded_file, 'graded': False}
            )
            messages.success(request, f'Your submission for "{task.title}" was successful!')
        except Task.DoesNotExist:
            messages.error(request, 'An error occurred. The selected task could not be found.')
        
        return redirect('tasks_page')

    # Query to get tasks that are not past their deadline
    # This part runs for ALL users (logged-in or not)
    active_tasks = Task.objects.filter(
        Q(deadline__isnull=True) | Q(deadline__gte=timezone.now())
    ).order_by('-id')

    user_submissions = []
    if request.user.is_authenticated:
        # Only query for completed tasks if the user is logged in
        user_submissions = Submission.objects.filter(user=request.user).values_list('task_id', flat=True)

    context = {
        'tasks': active_tasks,
        'completed_tasks': list(user_submissions),
    }
    return render(request, 'tasks.html', context)

def leaderboard(request):
    """
    Calculates and displays the leaderboard.

    This robust version starts with all active, non-superuser users,
    ensuring no one is missed, even if their profile is incomplete.
    """
    
    # Get all active, non-superuser users and calculate their score in a single, efficient query.
    # Coalesce ensures that users with no submissions get a score of 0 instead of None.
    users_with_scores = User.objects.filter(
        is_superuser=False,
        is_active=True
    ).annotate(
        total_score=Coalesce(Sum('submission__marks'), 0)
    ).filter(total_score__gt=0)  # Only include users with a score greater than 0

    ranked_users = list(users_with_scores)
    profiles = {
        profile.username: profile
        for profile in TaskZero.objects.filter(username__in=[user.username for user in ranked_users])
    }

    leaderboard_data = []
    for user in ranked_users:
        profile = profiles.get(user.username)

        # --- START OF FIX ---
        # Check if a profile was found. If not, profile will be None.
        if profile:
            # Profile exists, so it's safe to get attributes
            # We also check if the names or colgName fields are empty
            display_name = profile.names or (user.first_name or user.username)
            college_name = profile.colgName or "Not Specified"
            avatar = profile.avatar
        else:
            # This user has a score but no profile. Use fallback data.
            display_name = user.first_name or user.username # Use first_name, or username if that's empty
            college_name = "Not Specified"
            avatar = "fox"
        # --- END OF FIX ---

        leaderboard_data.append({
            'name': display_name,
            'college': college_name,
            'score': user.total_score,
            'avatar': avatar,
        })

    # Sort the list by score (highest first)
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)

    # Take the top 30 from the sorted list
    top_30_leaderboard = leaderboard_data[:30]

    return render(request, "leaderboard.html", {"leaderboard_data": top_30_leaderboard})
