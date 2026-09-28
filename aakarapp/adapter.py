from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        This function runs after a user authenticates with Google,
        but before the final login happens.
        """
        # Get the user data from Google
        google_user = sociallogin.user
        email = google_user.email

        # --- Main Logic ---
        try:
            # Check if a user with this email already exists in our database
            local_user = User.objects.get(email__iexact=email)
            
            # If the user exists, we connect the Google account to them.
            # This is the crucial step that allows them to log in.
            sociallogin.connect(request, local_user)

        except User.DoesNotExist:
            # If no user with this email exists, they are not registered.
            # We stop the login and show an error message in the modal.
            messages.error(request, f"The Google account for {email} is not registered. Please create an account first.")
            raise ImmediateHttpResponse(redirect('home'))