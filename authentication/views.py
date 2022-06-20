from urllib import request
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import auth
from curses.ascii import isalpha, isdigit, islower, isupper


def register(request: request) -> User:
    """Create a new user"""
    if request.method == 'GET':
        return render(request, 'register.html')

    # Get data from post
    if request.method == 'POST':
        firs_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')

        # Confirm password check
        if password != confirm_password:
            messages.add_message(request, constants.ERROR, 'Passwords does not match.')
            return redirect('/auth/register')
        
        # Avoid empty values on username and password
        if len(username.strip()) == 0 or len(password.strip()) == 0:
            messages.add_message(request, constants.ERROR, "Username an password can't be empty.")
            return redirect('/auth/register')

        # Check if username already exists
        user = User.objects.filter(username=username)
        if user.exists():
            messages.add_message(request, constants.ERROR, "User already exists.")
            return redirect('/auth/register')
        
        # Check for valid email (simple string check)
        if '@' not in request.POST.get('email'):
            messages.add_message(request, constants.ERROR, "Enter a valid mail.")
            return redirect('/auth/register')
        mail = User.objects.filter(email=email)

        if mail.exists():
            messages.add_message(request, constants.ERROR, "This email is already registered.")
            return redirect('/auth/register')

        # Save new user
        try:
            user = User.objects.create(username = username)
            user.set_password(password)
            user.first_name = firs_name
            user.last_name = last_name
            user.email = email
            user.save()

            return redirect('/auth/login')
        except:
            messages.add_message(request, constants.ERROR, "Internal error. Can't create user.")
            return redirect('/auth/register')
 
def login(request):
    """Main authentication method"""
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/home')    
        return render(request, 'login.html')
    
    # Get credentials from request.POST values
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check credentials and authenticate the user
        user = auth.authenticate(username=username, password=password)
        if not user:
            messages.add_message(request, constants.ERROR, "Invalid user or password")
            return render(request, 'login.html')
        else:
            auth.login(request, user)
            return redirect('/home')

def logout(request):
    """Main deauthentication method"""
    auth.logout(request)
    return redirect('/auth/login')
    
# TODO change password
def update_profile(request):
    """Update user data."""
    if request.method == 'GET':
        user = User.objects.get(id=request.user.id)
        return render(request, 'update_profile.html', context={'user': user})
    
    # Get user data from request.POST
    if request.method == 'POST':
        request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')

        # Check for an existing username
        user = User.objects.filter(username=username).exclude(id=request.user.id)
        if user.exists():
            messages.add_message(request, constants.ERROR, "Username already exists.")
            return redirect('/auth/update_profile')
        
        # Avoid empty values in username field
        if len(username) == 0:
            messages.add_message(request, constants.ERROR, "Username must not be empty.")
            return redirect('/auth/update_profile')

        # Save new data
        user = User.objects.get(id=request.POST.get('user_id'))
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.save()
        
        messages.add_message(request, constants.SUCCESS, "Profile updated!")
        return render(request, 'update_profile.html', context={'user': user})
        
# Hard coding password validation
def valid_password(password: str) -> bool:
    # Minimum 8 characters
    if len(password) < 8:
        return False

    # Letters, numbers, lowercase, uppercase and Symbols
    s = lambda x: x in ['$', '#', '!', '?', '-', '_', '&', '*', '@']
    if not any(isdigit(p) for p in password) or\
       not any(isalpha(p) for p in password) or\
       not any(islower(p) for p in password) or\
       not any(isupper(p) for p in password) or\
       not any(s(p) for p in password):
        return False

    else:
        return True

