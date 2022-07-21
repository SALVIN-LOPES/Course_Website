import imp
import json
from os import stat
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm 
# from .forms import *
from .models import *
from django.db.models import Q
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.parsers import FileUploadParser,FormParser,JSONParser,MultiPartParser
from rest_framework.response import Response

# -----------------------API VIEWS-----------------------
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CourseSerializer, LoginSerializer, UserSerializer,RegisterSerializer
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from django.contrib.auth import get_user_model
import requests

# from course_website.base import serializers

from .utils import *
from .permissions import *

# --------------------------------------API----------------------------
@api_view(["POST"])
def registerAPI(request):
    if not request.user.is_authenticated:
        data = request.data
        ser = RegisterSerializer(data=data)
        ser.is_valid(raise_exception=True)
        validated_data = ser.data
        user = ser.create(validated_data)
        user_json = {
        "username":user.username,
        "email":user.email,
        "is_staff":user.is_staff,
        }
        user_token = create_jwt_token(user)
        return JsonResponse({"msg":"User created","user_data":user_json,"token":user_token},status=200)
    return JsonResponse({"msg":"User already logged in!!!!!"},status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profileAPI(request):
    user = request.user
    user_json = {
        "username":user.username,
        "email":user.email,
        "is_staff":user.is_staff,
    }
    return JsonResponse(user_json,status=200)

@api_view(["POST"])
def loginAPI(request):
    ser = LoginSerializer(data = request.data)
    ser.is_valid(raise_exception=True)
    data = ser.data
    user = authenticate(request,username = data["username"],password = data["password"])
    if user:
        user_token = create_jwt_token(user)
        user_json = {
        "username":user.username,
        "email":user.email,
        "is_staff":user.is_staff,
        }
        return JsonResponse({"msg":"User login successful","user_data":user_json,"token":user_token},status=200)
    return JsonResponse({"msg":"Username and password does not match"},status=400)

@api_view(["POST"])
@permission_classes([IsEducator])
@parser_classes([MultiPartParser,FormParser,JSONParser]) 
def createCourseAPI(request):
    data = request.data
    user = request.user
    print("USER = ",user)
    print("is_staff = ",user.is_staff)
    if user.is_staff:
        data["educator"] = user.id
        file = request.FILES.get('image')
        # print(file)
        ser = CourseSerializer(data=data)
        ser.is_valid(raise_exception=True)
        ser_data = ser.validated_data
        # print(ser_data)
        course = ser.save()
        course_json = {
            "educator":request.user.username,
            "name":course.course_name,
            "description":course.description,
            # "image":course.image,
            "created":course.created,
        }
        print("COURSE = ",course)
        return JsonResponse({"msg":"course created","course":course_json},status=200)
    return JsonResponse({"msg":"you are not educator to create courses"},status = 400)

@api_view(['GET'])
def getUser(request,pk):
    if request.user.is_authenticated:
        # User = get_user_model()
        user = User.objects.get(id = pk)
        serializers = UserSerializer(user,many = False)
        user_token = create_jwt_token(user)
        print("USER = ",user)
        # return JsonResponse({"msg":"get user","user":user_json},safe=False)
        return Response(serializers.data)


@api_view(['GET'])
def getUsers(request):
    if request.user.is_authenticated:

        User = get_user_model()
        users = User.objects.all()
        all_users = []
        for user in users:
            user_token = create_jwt_token(user)
            user_json  ={
                "username": user.username,
                "email":user.email,
                "is_staff":user.is_staff,
                "user_token":user_token
            }
            all_users.append(user_json)
        
        if len(all_users) != 0:
            print("all_users",all_users)
            return JsonResponse({"msg":"displaying all users","users":all_users},status=200)
        return JsonResponse({"msg":"error while getting users"},status=400)
    return JsonResponse({"msg":"you dont have permission for user details"},status=400)


@api_view(['GET'])
@permission_classes([IsUser])
def getCourses(request):
    if request.user.is_authenticated :
        courses = Course.objects.all()
        base_url =  "{0}://{1}/media/".format(request.scheme, request.get_host())
        print("baseurl = ",base_url)
        all_courses = []
        for course in courses:
            if course:
                course_json = course.toJson(base_url)
                all_courses.append(course_json)
        return JsonResponse({"msg":"list of courses","courses":all_courses},safe = False)
    return JsonResponse({"msg":"you dont have permission to access the courses"},status=400)

@api_view(['POST'])
@permission_classes([IsUser])
def enrollCourse(request):
    user = request.user
    data = request.data
    course_id = data.get("course_id","")
    course = Course.objects.filter(id=course_id).first()
    
    if course:
        enroll = EnrollModel.objects.filter(user=user,course=course).first() # where user=user and course=course
        if enroll is None:
            enroll = EnrollModel(user=user,course=course)
            enroll.save()
            return JsonResponse({"msg":"You have successfully enrolled","data":enroll.toJson(request)},status=400)
        return JsonResponse({"msg":"You have already enroll in this course"},status=400)
    return JsonResponse({'Msg':"course doesnot exist"},status=400)

@api_view(['GET'])
@permission_classes([IsUser])
def allEnrollCourses(request):
    user = request.user
    enrolls = EnrollModel.objects.filter(user=user)
    courses_list = []
    base_url =  "{0}://{1}/media/".format(request.scheme, request.get_host())
    for enroll in enrolls:
        course_json = enroll.course.toJson(base_url)
        courses_list.append(course_json)
    return JsonResponse({"data":courses_list},status=200)


def userToProfile(user):
    return {
                "username": user.username,
                "email":user.email,
                "is_staff":user.is_staff,
    }


@api_view(['GET'])
@permission_classes([IsEducator])
def getEnrolledUsers(request,pk):
    user = request.user
    course = Course.objects.filter(id = pk).first()
    if course:
        if user == course.educator:
            enrolls = EnrollModel.objects.filter(course=course)
            users_list = []
            for enroll in enrolls:     
                user_json = userToProfile(enroll.user)   
                users_list.append(user_json)
            return JsonResponse({"data":users_list},status=200)
        return JsonResponse({"msg":"user doesnot have permission"},status=400)
    return JsonResponse({"msg":"course doesnot exist"},status=400)

    
    
@api_view(['GET'])
@permission_classes([IsEducator])
def getEducatorCourse(request):
    user = request.user
    courses_educator = Course.objects.filter(educator = user)
    all_courses_educator = []
    for course in courses_educator:
        course_json = course.toJson(request)
        all_courses_educator.append(course_json)
    
    return JsonResponse({"msg":"the particular educator courses","courses":all_courses_educator},status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getCourseDetailApi(request,pk):
    user = request.user
    course = Course.objects.filter(id=pk).first()
    if course:
        if not user.is_staff or user==course.educator:
            base_url =  "{0}://{1}/media/".format(request.scheme, request.get_host())
            return JsonResponse({"data":course.toJson(base_url)},status=400) 
        return JsonResponse({"msg":"does not have permission"},status=400)
    return JsonResponse({"msg":"does not found the course"},status=400)


        



            



