from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name = 'account'

urlpatterns = [
    path('signout/', views.signout, name='signout'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('settings/', views.settings_page, name='settings'),
    path('change.avatar/', views.select_avatar, name='select_avatar'),
    path('send_correction/', views.send_correction, name='send_correction'),
    path('activate/<uidb64>/<token>', views.activate_email, name='activate'),

    path('password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='account/password/password_reset_form.html',
            email_template_name='account/password/password_reset_email.html',
            success_url = reverse_lazy('account:password_reset_done')
        ),
        name='password_reset'
    ),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password/password_reset_complete.html'), name='password_reset_complete')
]
