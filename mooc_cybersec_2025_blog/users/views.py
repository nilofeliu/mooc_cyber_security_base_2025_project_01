# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, ProfileUpdateForm, ThoughtForm
from .models import Profile, Thought
from django.contrib.auth.models import User
from django.db import connection

# The registration view that the server is looking for
def register(request):
    if request.user.is_authenticated:
        return redirect('user_page')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # This creates the profile for new users
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("user_page")
    else:
        form = RegistrationForm()
    return render(request=request, template_name="users/register.html", context={"register_form": form})


@login_required
def user_page(request):
    # FLAW 1: Broken Access Control - any user can view any user's profile
    user_id = request.GET.get('user_id', request.user.id)
    # Fix 
    # user_id = request.user.id

    try:
        target_user = User.objects.get(id=user_id)
        profile, created = Profile.objects.get_or_create(user=target_user)
    except User.DoesNotExist:
        target_user = request.user
        profile, created = Profile.objects.get_or_create(user=request.user)


    
    # Initialize forms BEFORE the POST handling
    p_form = ProfileUpdateForm(instance=profile)
    t_form = ThoughtForm()
    
    if request.method == 'POST':
        if 'update_picture' in request.POST:
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, 'Your profile picture has been updated!')
                return redirect('user_page')
        elif 'post_thought' in request.POST:
            t_form = ThoughtForm(request.POST)
            if t_form.is_valid():
                thought = t_form.save(commit=False)
                thought.user = request.user
                thought.save()
                messages.success(request, 'Your thought has been shared!')
                return redirect('user_page')

    # FLAW 1: Shows any user's thoughts
    thoughts = Thought.objects.filter(user=target_user).order_by('-created_at')
    # FIX (commented): Only show current user's thoughts
    # thoughts = Thought.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'p_form': p_form,
        't_form': t_form,
        'thoughts': thoughts,
        'target_user': target_user
    }
    return render(request, 'users/user_page.html', context)


def flaw_sql_injection(request):
    thought = None
    # FLAW 3 - Injection
    if request.GET.get('id'):
        thought_id = request.GET.get('id')
        with connection.cursor() as cursor:
            query = f"SELECT id, text FROM users_thought WHERE id = {thought_id}"
            print(f"DEBUG - SQL Query: {query}")  # Add this debug line
            cursor.execute(query)
            thought = cursor.fetchall() # change this to get all results
            print(f"DEBUG - Result: {thought}")  # Add this debug line
    
    return render(request, 'users/thought.html', {'thought': thought})

# FIX For Flaw 3
#  def flaw_sql_injection(request):
#      thoughts = None
#      if request.GET.get('id'):
#          thought_id = request.GET.get('id')
#          try:
#              thought_id = int(thought_id)  # Validate input
#              with connection.cursor() as cursor:
#                  query = "SELECT id, text FROM users_thought WHERE id = %s"
#                  cursor.execute(query, [thought_id])
#                  thoughts = cursor.fetchone()
#          except ValueError:
#              thoughts = None  # Handle invalid input
     
#      return render(request, 'users/thought.html', {'thoughts': thoughts})
