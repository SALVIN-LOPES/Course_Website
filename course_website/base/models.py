
from statistics import mode
from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    educator = models.ForeignKey(User,on_delete=models.CASCADE,related_name="educator")
    course_name = models.CharField(max_length=1000)
    description = models.TextField(null = True,blank=True)
    image = models.ImageField(null=True, blank=True,upload_to='courses')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def toJson(self,request):
        base_url =  "{0}://{1}/media/".format(request.scheme, request.get_host())
        return {
            "id":self.id,
            "educator":{
                "username": self.educator.username,
                "email":self.educator.email,
                "is_staff":self.educator.is_staff,
            },
            "course_name":self.course_name,
            "description":self.description,
            "image":base_url+str(self.image)
        }

    class Meta:
        ordering = ['-updated','-created']

    def __str__(self):
        return self.course_name[0:50]

class EnrollModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user")
    course = models.ForeignKey(Course,on_delete=models.CASCADE,related_name='courses')
    enroll_date = models.DateTimeField(auto_now_add=True)

    def toJson(self,request):
        
        return {
            "id":self.id,
            "user":{
                "username": self.user.username,
                "email":self.user.email,
                "is_staff":self.user.is_staff,
            },
            "couser":self.course.toJson(request),
            "enroll_date":str(self.enroll_date),
        }
    def __str__(self):
        return str(self.user) + f' is enrolled to ' + str(self.course)


