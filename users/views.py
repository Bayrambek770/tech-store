from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings

from .forms import LoginForm, CustomUserCreationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            # Session expiry: if not remember -> browser session only
            if not form.cleaned_data.get('remember'):
                request.session.set_expiry(0)
            messages.success(request, 'Logged in successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'registration/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()  # Do NOT log the user in automatically
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'registration/signup.html', {'form': form})