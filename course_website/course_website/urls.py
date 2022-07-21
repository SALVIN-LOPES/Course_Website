
from django.contrib import admin
from django.urls import path,include
from rest_framework.authtoken import views
from base import views,serializers
from rest_framework.routers import DefaultRouter
from django.conf import settings  
from django.conf.urls.static import static  


urlpatterns = [
  path('admin/', admin.site.urls),
  path('api/',include('base.urls')),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)  