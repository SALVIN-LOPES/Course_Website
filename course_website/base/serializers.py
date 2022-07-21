

from dataclasses import fields
from rest_framework import serializers,viewsets 
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import *


class UserSerializer(serializers.ModelSerializer):

  class Meta:
    model = User
    fields = ["username","email","is_staff"]

#Serializer to Register User
class RegisterSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(
    required=True,
    validators=[UniqueValidator(queryset=User.objects.all())]
  )
  password = serializers.CharField(
    required=True, validators=[validate_password])
  password2 = serializers.CharField(write_only=True, required=True)
  is_staff = serializers.BooleanField(default=False)
  class Meta:
    model = User
    fields = ('username', 'password', 'password2',
         'email','is_staff')
    extra_kwargs = {
      'first_name': {'required': True},
      'last_name': {'required': True}
    }
  def validate(self, attrs):
    if attrs['password'] != attrs['password2']:
      raise serializers.ValidationError(
        {"password": "Password fields didn't match."})
    return attrs
  def create(self, validated_data):
    user = User.objects.create(
      username=validated_data['username'],
      email=validated_data['email'],
      is_staff = validated_data["is_staff"]
    )
    user.set_password(validated_data['password'])
    user.save()
    return user

class LoginSerializer(serializers.Serializer):
  username = serializers.CharField(required=True)
  password = serializers.CharField(required=True)

class CourseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = ('educator','image', 'course_name', 'description')

    

    
    




