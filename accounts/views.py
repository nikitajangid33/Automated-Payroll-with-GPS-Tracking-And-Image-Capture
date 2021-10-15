from django.contrib import messages
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User,auth
from .models import Employee,WorkLocations,EmployeeWorkLocations,EmployeeImages
from .serializers import EmployeeSerializer,UserSerializer


# Create your views here.


def registerView(request):
    return render(request,'register.html')

#registerAdmin by HR using name email and password
def register(request):
    firstname=request.POST['first_name']
    lastname=request.POST['last_name']
    username=request.POST['username']
    email=request.POST['email']
    password1=request.POST['password']
    password2=request.POST['confirmPassword']

    data={'username':username,'first_name':firstname,'last_name':lastname,'email':email,'password':password1}
    serializer=UserSerializer(data=data)
    print(serializer.is_valid())
    print(len(username))

    if password1 == password2:#checking if both the password is same or not
        if User.objects.filter(username=username).exists():#checking if username is already exist in DB
            messages.info(request,'Username taken')
            return HttpResponse('Username is taken',content_type='application/json')#returns an error

        else:
            #else creating the userAdmin with is_active true by default
            user=User.objects.create_user(username=username,first_name=firstname,last_name=lastname,email=email,password=password1)

            user.save()
            print('success')
            messages.info(request,'Success')
            return HttpResponse('User is registered Successfuly',content_type='application/json')
    else:
        #if password does not matches then returns an error
        return HttpResponse('password not matches ',content_type='application/json')


#login UserAdmin using username and password
def login(request):
    username=request.POST['username']
    password=request.POST['password']
    user=auth.authenticate(username=username,password=password)

    if user is not None:
        #auth.login(request,user)
        return HttpResponse('User login successfuly',content_type='application/json')
    else:
        return HttpResponse('Invalid username/password',content_type='application/json')

def registerEmployee(request):
    firstname=request.POST['first_name']
    lastname=request.POST['last_name']
    email=request.POST['email']
    password=request.POST['password']
    street=request.POST['street']
    pincode=request.POST['pincode']
    country=request.POST['country']
    mobileNumber=request.POST['mobileNumber']
    empAdmin=request.POST['empAdmin']

    if Employee.objects.filter(email=email).exists():
        return HttpResponse('{"status":"Email already taken"}',content_type='application/json')
    else:
        user=User.objects.filter(id=empAdmin).get()
        print(user.id)
        if not User.objects.filter(id=empAdmin).exists():
            return HttpResponse('Employee Id is wrong',content_type='application/json')
        else:
            employee=Employee.objects.create(fname=firstname,lname=lastname,email=email,password=password,street=street,pincode=pincode,country=country,mobileNumber=mobileNumber,empAdmin=user)
            employee.save()
            return HttpResponse('{"status":"Employee is registered Successfuly"}',content_type='application/json')

def saveWorkLocation(request):
    address=request.POST['address']
    pincode=request.POST['pincode']
    country=request.POST['country']
    state=request.POST['state']
    initialLongitude=request.POST['initialLongitude']
    initialLatitude=request.POST['initialLatitude']
    finalLongitude=request.POST['finalLongitude']
    finalLatitude=request.POST['finalLatitude']

    workloc=WorkLocations.objects.create(address=address,pincode=pincode,country=country,state=state,initialLatitude=initialLatitude,initialLongitude=initialLongitude,finalLatitude=finalLatitude,finalLongitude=finalLongitude)
    workloc.save()
    return HttpResponse('WorkLocation created successfuly',content_type='application/json')


def saveEmployeeCurrentLocation(request):
    currentLongitude=request.POST['currentLongitude']
    currentLatitude=request.POST['currentLatitude']
    empId=request.POST['empId']
    workLocationId=request.POST['workLocationId']

    emp=Employee.objects.filter(id=empId).get()
    print(emp.id)
    if not Employee.objects.filter(id=empId).exists():
        return HttpResponse('Employee Id is wrong',content_type='application/json')
    
    workLoc=WorkLocations.objects.filter(id=workLocationId).get()
    print(workLoc)
    if not WorkLocations.objects.filter(id=workLocationId).exists():
        return HttpResponse('WorkLocation Id is wrong',content_type='application/json')

    empLoc=EmployeeWorkLocations.objects.create(empId=emp,workLocationId=workLoc,currentLatitude=currentLatitude,currentLongitude=currentLongitude)
    empLoc.save()
    return HttpResponse('Data Saved succcessfuly',content_type='application/json')


def saveEmployeeImage(request):
    empId=request.POST['empId']
    img=request.POST['img']
    emp=Employee.objects.filter(id=empId).get()
    print(emp.id)
    if not Employee.objects.filter(id=empId).exists():
        return HttpResponse('Employee Id is wrong',content_type='application/json')

    
    empImg=EmployeeImages.objects.create(empId,empId,img=img)
    empImg.save()
    return HttpResponse('Date Saved succcessfuly',content_type='application/json')