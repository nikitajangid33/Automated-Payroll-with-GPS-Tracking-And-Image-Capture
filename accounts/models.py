from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.contrib.auth.models import User
from django.utils.timezone import datetime

# Create your models here.

class Employee(models.Model):
    fname=models.CharField(max_length=50)
    lname=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=128,default='abcd1234')
    street=models.CharField(max_length=50)
    pincode=models.IntegerField(default=000000)
    state=models.CharField(max_length=10)
    country=models.CharField(max_length=10)
    mobileNumber=models.DecimalField(max_digits=10,decimal_places=0)
    created_at=models.DateTimeField(default=datetime.now)
    empAdmin=models.ForeignKey(User,on_delete=models.CASCADE)

class WorkLocations(models.Model):
    address=models.CharField(max_length=100)
    pincode=models.IntegerField(default=000000)
    state=models.CharField(max_length=10)
    country=models.CharField(max_length=10)
    initialLongitude=models.DecimalField(max_digits=9,decimal_places=6)
    initialLatitude=models.DecimalField(max_digits=9,decimal_places=6)
    finalLongitude=models.DecimalField(max_digits=9,decimal_places=6)
    finalLatitude=models.DecimalField(max_digits=9,decimal_places=6)
    created_at=models.DateField(default=datetime.now)
    active=models.BooleanField(default=True)

class EmployeeWorkLocations(models.Model):
    empId=models.ForeignKey(Employee,on_delete=models.CASCADE)
    workLocationId=models.ForeignKey(WorkLocations,on_delete=models.CASCADE)
    currenLatitude=models.DecimalField(max_digits=9,decimal_places=6)
    currenLongitude=models.DecimalField(max_digits=9,decimal_places=6)
    updated_at=models.DateTimeField(default=datetime.now)

class EmployeeImages(models.Model):
    empId=models.ForeignKey(Employee,on_delete=models.CASCADE)
    img=models.ImageField(upload_to='pics')
    saveDateTime=models.DateTimeField(default=datetime.now)
    is_verified=models.BooleanField(default=False)