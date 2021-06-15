from .views import RegistrationView, UsernameValidationView, EmailValidationView, VerificationView, LoginView, LogoutView, RequestPasswordResetEmail, CompletePasswordReset
from django.urls import path
from django.views.decorators.csrf import csrf_exempt, csrf_protect

app_name = 'authenticate'
urlpatterns = [
    path('registration', RegistrationView.as_view(), name="registration"),
    path('validate-username', UsernameValidationView.as_view(),
         name="validate-username"),
    path('validate-email', EmailValidationView.as_view(),
         name="validate-email"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate"),
    path('', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('request-reset-link', RequestPasswordResetEmail.as_view(),
         name="request-password"),
    path('set-new-password/<uidb64>/<token>',
         CompletePasswordReset.as_view(), name="reset-user-password"),
]
