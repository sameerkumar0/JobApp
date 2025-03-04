from django.shortcuts import render, redirect,HttpResponse
from django.contrib import messages,auth
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password
from .models import User, PendingUser  
from common.tasks import send_email  
from datetime import datetime, timezone




def home(request):
    return render(request,'base.html')

def login(request):
    if request.method=="POST":
        email:str=request.POST.get('email')
        password=request.POST.get('password')
        user=auth.authenticate(request,email=email,password=password)
        if user is not None:
            auth.login(request,user)
        else:
            messages.error(request,"invalid credentials")
            return redirect('login')


    else:
        return render(request,'login.html')

def register(request):
    if request.method == "POST":
        email = request.POST['email'].lower()  
        username = request.POST['username']
        password = request.POST['password']

        # Check if the user already exists in the User table
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        # Check if the email is already in PendingUser table
        pending_user = PendingUser.objects.filter(email=email).first()
        if pending_user:
            messages.error(request, "A verification email has already been sent. Please check your inbox.")
            return redirect("register")

        # Generate a verification code
        verification_code = get_random_string(10)

        # Create a new PendingUser
        PendingUser.objects.create(
            email=email,
            username=username,
            password=make_password(password),
            verification_code=verification_code,
            created_at=datetime.now(timezone.utc) 
        )

        # Send verification email using SMTP
        send_email(
            subject='Verify Your Account',
            email_to=[email],
            html_template='emails/email_verification_template.html',
            context={'code': verification_code}
        )

        messages.success(request, f"Verification code sent to {email}")
        return render(request, "verify_account.html", context={'email': email})

    return render(request, "register.html")

def verify_account(request):
    if request.method == "POST":
        code = request.POST['code']
        email = request.POST['email']

        pending_user = PendingUser.objects.filter(verification_code=code, email=email,).first()

        if pending_user and pending_user.is_valid():
            user = User.objects.create(
                email=pending_user.email,
                password=pending_user.password,
                username=pending_user.username
            )
            pending_user.delete()  # Remove the pending user after successful verification
            auth.login(request, user)  # Log in the user
            messages.success(request, "Account verified successfully!")
            return redirect('home')

        else:
            messages.error(request, "Invalid verification code")
            return render(request, 'verify_account.html', {'email': email}, status=400)

    return HttpResponse("Invalid request", status=400)