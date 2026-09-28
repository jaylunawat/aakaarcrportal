from django.urls import path, include
from . import views

urlpatterns = [
    # Main page URL
    path('', views.home, name="home"),

    # --- NEW: URL for the Tasks Page ---
    path('tasks', views.tasks_page, name='tasks_page'),

    # User Authentication and Profile URLs
    path('register', views.register_cr, name="register_cr"),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('dashboard', views.dashboard, name="dashboard"),
    path('updateProfile', views.updateProfile, name="updateProfile"),
    
    # Other pages
    path('leaderboard', views.leaderboard, name='leaderboard'),
    
    # --- REMOVED ---
    # The old, repetitive task submission URL has been removed.
    # The allauth urls might be unnecessary now, but we'll leave them for now
    # to avoid breaking anything.
    path('accounts/', include('allauth.urls')),
]