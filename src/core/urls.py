from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from scm.forms import MyAuthenticationForm
from scm.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(authentication_form=MyAuthenticationForm), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/changepassword/', home.change_password, name='change_password'),
    path('accounts/setpassword/', home.setpassword, name='setpassword'),
    path('accounts/signup/', home.SignUpView.as_view(), name='signup'),
    path('', include('scm.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
