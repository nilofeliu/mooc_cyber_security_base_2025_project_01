# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.user_page, name='user_page'),
    path('register/', views.register, name='register'),

    # This line is the crucial one.
    # It defines the URL for the user page and gives it the name 'user_page'.
    path('profile/', views.user_page, name='user_page'),
    
]

# We use the URL *name* from users/urls.py, which is 'user_page'.
LOGIN_REDIRECT_URL = 'user_page'

# It's also good practice to tell Django where to go after logging out.
# We'll send them back to the login page.
LOGOUT_REDIRECT_URL = 'login'