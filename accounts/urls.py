from django.urls import path
from .views import LoginView, change_language


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path('change_language/<str:language>',
         change_language, name='change_language'),
]
