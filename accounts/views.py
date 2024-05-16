from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

# Create your views here.


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
