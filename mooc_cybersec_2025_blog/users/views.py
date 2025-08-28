# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm, ProfileUpdateForm, ThoughtForm
from .models import Profile, Thought

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


# The secure and robust user page view
@login_required
def user_page(request):
    # This line fixes the "User has no profile" error for old users
    profile, created = Profile.objects.get_or_create(user=request.user)

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
    else:
        p_form = ProfileUpdateForm(instance=profile)
        t_form = ThoughtForm()

    thoughts = Thought.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'p_form': p_form,
        't_form': t_form,
        'thoughts': thoughts
    }
    return render(request, 'users/user_page.html', context)
