from django.urls import path
from django.contrib.auth import views as auth_views
from .views import login_view, register_view
from .forms import StyledPasswordResetForm, StyledSetPasswordForm

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    # Password reset flow
    path('password-reset/',
         auth_views.PasswordResetView.as_view(form_class=StyledPasswordResetForm, template_name='registration/password_reset_form.html'),
        name='password_reset'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(form_class=StyledSetPasswordForm, template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),
]