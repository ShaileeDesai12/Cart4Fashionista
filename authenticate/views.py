from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading

# Create your views here.


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authenticate/registration.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        # password2 = request.POST['password2']
        context = {
            'fieldValues': request.POST,
        }
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 8:
                    messages.error(
                        request, 'Password must be atleast 8 characters.')
                    return render(request, 'authenticate/registration.html', context)
                else:
                    user = User.objects.create_user(
                        username=username, email=email)
                    user.set_password(password)
                    user.is_active = False
                    user.save()
                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    domain = get_current_site(request).domain
                    link = reverse('authenticate:activate', kwargs={
                                   'uidb64': uidb64, 'token': token_generator.make_token(user)})
                    activation_url = 'http://' + domain + link
                    email_subj = 'Activate your account!'
                    email_body = 'Hello ' + user.username + \
                        "! Thank you for registering with us!\n" + \
                        'We are happy to have you. ' + \
                        'You are just one more step away. ' + \
                        "We need to know that it's really you.\n" + \
                        'Click on the link below to activate your account. \n' + \
                        activation_url
                    email = EmailMessage(
                        email_subj,
                        email_body,
                        'noreply@cart4fashionista.com',
                        [email],
                    )
                    EmailThread(email).start()
                    messages.success(
                        request, 'Congratulations! Your Account has been successfully created!')
                    messages.info(
                        request, 'Please check your email for activation link.')
                    return render(request, 'authenticate/registration.html')


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'Username should only contain Alphanumeric characters!'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry! This Username is already in use.'}, status=409)
        if len(str(username)) < 3:
            return JsonResponse({'username_error': 'Username too short! It must be atleast 3 characters.'}, status=400)
        return JsonResponse({'username_valid': True})


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Please enter a valid Email address!'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry! This email is already in use.'}, status=409)
        else:
            return JsonResponse({'email_valid': True})


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return redirect('authenticate:login' + '?message=' + 'User already activated')
            if user.is_active:
                return redirect('authenticate:login')
            else:
                user.is_active = True
                user.save()
                messages.success(
                    request, 'Your account has been activated! Login to continue.')
                return redirect('authenticate:login')
        except Exception as ex:
            pass
        return redirect('authenticate:login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authenticate/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = auth.authenticate(username=username, password=password)
            print(user)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username + '! You are now logged in.')
                    return redirect('shop:ShopHome')
                else:
                    messages.error(
                        request, 'Your account is not activated. Please check your email for verification link.')
                    return render(request, 'authenticate/login.html')
            else:
                messages.error(
                    request, 'Invalid Credentials! Please try again.')
                return render(request, 'authenticate/login.html')
        else:
            messages.error(request, 'Please fill all fields!')
            return render(request, 'authenticate/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out!')
        return redirect('authenticate:login')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authenticate/reset-password.html')

    def post(self, request):
        email = request.POST['email']
        context = {
            'values': request.POST,
        }
        if not validate_email(email):
            messages.error(request, 'Please enter a valid Email!')
            return render(request, 'reset-password.html', context)
        else:
            current_site = get_current_site(request)
            user = User.objects.filter(email=email)
            if user.exists():
                email_contents = {
                    'user': user[0],
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                    'token': PasswordResetTokenGenerator().make_token(user[0]),
                }
                link = reverse('authenticate:reset-user-password', kwargs={
                               'uidb64': email_contents['uid'], 'token': email_contents['token']})
                reset_url = 'http://' + str(current_site) + link
                email_subj = 'Reset your Password!'
                email_body = 'Hello there,' + \
                    'Click on the link below to reset your password. \n' + \
                    reset_url
                email = EmailMessage(
                    email_subj,
                    email_body,
                    'noreply@inexpensible.com',
                    [email],
                )
                EmailThread(email).start()
            messages.success(
                request, 'Please check your email for reset link.')
            return render(request, 'authenticate/reset-password.html')


class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.warning(
                    request, 'This link has already been used once!')
                return render(request, 'reset-password.html')
        except Exception as identifier:
            pass
        return render(request, 'authenticate/set-newpassword.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        password = request.POST['password']
        password2 = request.POST['password2']
        if password != password2:
            messages.warning(request, "Both Passwords don't match!")
            return render(request, 'authenticate/set-newpassword.html', context)

        if len(password) < 8:
            messages.error(
                request, "Password too short! It must be atleast 8 characters long.")
            return render(request, 'authenticate/set-newpassword.html', context)
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(
                request, 'Password reset successfully! You can login with the new password now.')
            return redirect('login')
        except Exception as identifier:
            messages.info(
                request, 'Something has gone wrong! Please try again.')
            return render(request, 'authenticate/set-newpassword.html', context)
