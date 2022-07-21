from django.contrib import admin
from django.urls import path,include
from . import views

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

  # ---------------------------API:URLS-----------------------
  path('register/',views.registerAPI,name = 'register'), 
  path('login/',views.loginAPI,name = 'login'), 
  path('create-course/',views.createCourseAPI,name = 'create_course'), 
  path('user-profile/',views.profileAPI,name = 'profile'), 
  path('get-users/',views.getUsers,name = 'get-users'), 
  path('get-user/<str:pk>/',views.getUser,name = 'get-user'), 
  path('get-courses/',views.getCourses,name = 'get-courses'), 
  path('get-enroll-courses/',views.allEnrollCourses,name = 'get-courses'),
  path('get-educator-course/',views.getEducatorCourse,name = 'get-educator-course'), 
  path('enroll-course/',views.enrollCourse,name = 'enroll-course'), 
  path('course-detail/<str:pk>/',views.getCourseDetailApi,name = 'enroll-course'),
  path('get-enrolled-users/<str:pk>/',views.getEnrolledUsers,name = 'get-enrolled-users'), 
   # Refresh the Jwt Access Token if refresh Token is Valid and also Return the new refresh token
  path('refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'), 

]