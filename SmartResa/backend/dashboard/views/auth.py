from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from ..forms import RegistrationForm, CustomLoginForm

def redirect_role_based_dashboard(user):
    if user.role == 'student':
        return redirect('student_dashboard')
    elif user.role == 'teacher':
        return redirect('teacher_dashboard')
    return redirect('admin_dashboard')
@csrf_protect
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Manually set the authentication backend
                user.backend = 'dashboard.backends.EmailAuthBackend'
                
                login(request, user)
                messages.success(request, "Registration successful!")
                return redirect_role_based_dashboard(user)
            except Exception as e:
                messages.error(request, f"Registration error: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
@csrf_protect
def custom_login(request):
    if request.user.is_authenticated:
        return redirect_role_based_dashboard(request.user)
        
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect_role_based_dashboard(user)
        messages.error(request, 'Invalid email or password')
    
    return render(request, 'registration/login.html', {
        'form': CustomLoginForm(),
        'title': 'Login to SmartResa'
    })

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('login')