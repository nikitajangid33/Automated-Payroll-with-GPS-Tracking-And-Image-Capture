from django.contrib import messages
from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User,auth
from django.contrib.auth.hashers import make_password,check_password
from .models import Employee,WorkLocations,EmployeeWorkLocations,EmployeeImages
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser,MultiPartParser 
import re
from datetime import datetime,timedelta
from django.utils import timezone



def registerView(request):
    return render(request,'register.html')


#################################################### User Admin CRUD operation Start ###################

#registerAdmin by HR using name email and password
def register(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    if all(k in finalRequest for k in ('first_name','last_name','username','email','email','password','confirmPassword')):
        firstname=request.POST['first_name']
        lastname=request.POST['last_name']
        username=request.POST['username']
        email=request.POST['email']
        password1=request.POST['password']
        password2=request.POST['confirmPassword']

        #check field is set of not
        if firstname and lastname and username and email and password1 and password2:
            print("all variables are set")
        else:
            return HttpResponse(
                '{"status":400,"message":"Required Fields cannot be empty"}',
                content_type='application/json'
            )

        #validating email using regular expression
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            print("Valid Email")
        else:
            return HttpResponse(
                '{"status":400,"message":"Email should be in valid format"}',
                content_type='application/json'
            )

        #validating username length
        if len(username) < 8:
            return HttpResponse(
                '{"status":400,"message":"Username length should have minimum length of 8"}',
                content_type='application/json'
            )

        #validating password length
        if len(password1) < 8:
            return HttpResponse(
                '{"status":400,"message":"Password length should have minimum length of 8"}',
                content_type='application/json'
            )

        #checking if both the password is same or not
        if password1 == password2:
            #checking if username is already exist in DB
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username taken')
                return HttpResponse('{"status":400,"message":"Username is taken."}',content_type='application/json')#returns an error

            else:
                #else creating the userAdmin with is_active true by default
                user=User.objects.create_user(username=username,first_name=firstname,last_name=lastname,email=email,password=password1)

                user.save()
                print('success')
                return HttpResponse('{"status":200,"message":"User registered successfuly."}',content_type='application/json')
        else:
            #if password does not matches then returns an error
            return HttpResponse('{"status":400,"message":"Password does not matches. Please check and Try again"}',content_type='application/json')
    else:
        return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')

#by default createUSer is not in staff first use to verify by superuser to make it as staff member

#login UserAdmin using username and password
def login(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    if all(k in finalRequest for k in ('username','password')):

        username=request.POST['username']
        password=request.POST['password']

        #check field is set of not
        if username and password:
            print("all variables are set")
        else:
            return HttpResponse(
                '{"status":400,"message":"All Fields are mandatory"}',
                content_type='application/json'
            )

        #authenticate the user using username and password 
        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return HttpResponse('{"status":200,"message":"User login successfuly."}',content_type='application/json')
        else:
            return HttpResponse('{"status":400,"message":"Invalid Username and password.Please check once again."}',content_type='application/json')
    else:
        return HttpResponse('{"status":400,"message":"Required Fields are missing in the request."}',content_type='application/json')


#update operation in User and Employee and WorkLocation(reusability of same function)
def update(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    #updatioIn can be EMployee or User only
    if 'updationIn' in finalRequest and request.POST['updationIn'] in ['User','Employee','WorkLocations']:
        updatePerformedIn=request.POST['updationIn']
    else:
        return HttpResponse('{"status":400,"message":"updationIn is mandatory.Possible values are Employee and User only"}',content_type='application/json')

    #checking if id is set in the request or else throw error
    if 'id' in finalRequest:
        userId=request.POST['id']
    else:
        return HttpResponse('{"status":400,"message":"Id is mandatory"}',content_type='application/json')

    fieldToBeUpdated={}

    #constructing a dictionary of non empty value for updation
    for key,value in finalRequest.items():
        if value:
            if key == 'password':
                value=make_password(value)#before storing the password hashing first
                print(value)
            if key =='updationIn':#do nothing as updationKey is used for table only
                continue
            fieldToBeUpdated[key]=value

    print(fieldToBeUpdated)

    if updatePerformedIn=='User':
        User.objects.filter(id=userId).update(**fieldToBeUpdated)
    elif updatePerformedIn=='Employee':
        Employee.objects.filter(id=userId).update(**fieldToBeUpdated)
    elif updatePerformedIn=='WorkLocations':
        WorkLocations.objects.filter(id=userId).update(**fieldToBeUpdated)

    return HttpResponse('{"status":200,"message":"Information updated Successfuly."}',content_type='application/json')


#checking is user has done the login 30 days before then consider that user inactive and update in DB
def inactiveUser(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    #checking if variables are set in the request or not
    if all (k in finalRequest for k in ('id')):
        userId=request.POST['id']#taking id from the user

        #checking if id is empty or not
        if userId:
            if User.objects.filter(id=userId).exists():
               User.objects.filter(id=userId).update(is_active=False)#updating to inactive
               return HttpResponse('{"status":200,"message":"Inactive the User successfuly"}',content_type='application/json')
            else:
               #user id does not exists
              return HttpResponse(
                '{"status":400,"message":"User Id does not exist in DB"}',
                content_type='application/json'
            )
        else:
            return HttpResponse(
                '{"status":400,"message":"User Id cannot be empty"}',
                content_type='application/json'
            )
    else:
        #checking how many user whose login time is 30days back..mark them inactive
        date30DaysBack=datetime.now(tz=timezone.utc) - timedelta(days=30)
        print(date30DaysBack)
       
        inactiveUsers=User.objects.filter(last_login__lte=date30DaysBack).get()
        print(inactiveUsers)
        User.objects.filter(id=inactiveUsers.id).update(is_active=False)#updating to inactive
        return HttpResponse('{"status":200,"message":"Inactivate the Users successfuly"}',content_type='application/json')

        


####################Employee CRUD operation start ######################################################################

#register Employee
def registerEmployee(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    print(finalRequest)
    #checking if all the fields are present in the request or not
    if all(k in finalRequest for k in ('first_name','last_name','email','street','password','pincode','country','mobileNumber','empAdmin')):

        firstname=request.POST['first_name']
        lastname=request.POST['last_name']
        email=request.POST['email']
        password=request.POST['password']
        street=request.POST['street']
        pincode=request.POST['pincode']
        country=request.POST['country']
        mobileNumber=request.POST['mobileNumber']
        empAdmin=request.POST['empAdmin']

        #check field is set of not
        if firstname and lastname and street and email and password and pincode and country and mobileNumber and empAdmin:
            print("all variables are set")
        else:
            return HttpResponse(
                '{"status":400,"message":"Required Fields cannot be empty"}',
                content_type='application/json'
            )

        #validating email using regular expression
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            print("Valid Email")
        else:
            return HttpResponse(
                '{"status":400,"message":"Email should be in valid format"}',
                content_type='application/json'
            )

        #validating username length
        if len(pincode) < 6:
            return HttpResponse(
                '{"status":400,"message":"Username length should have minimum length of 8"}',
                content_type='application/json'
            )

        #validating password length
        if len(password) < 8:
            return HttpResponse(
                '{"status":400,"message":"Password length should have minimum length of 8"}',
                content_type='application/json'
            )

        #checking if email already exist or not
        if Employee.objects.filter(email=email).exists():
            return HttpResponse('{"status":400,"message":"Email already taken"}',content_type='application/json')
        else:
            if not User.objects.filter(id=empAdmin).exists():
                return HttpResponse('{"status":400,"message":"Employee Id is wrong"}',content_type='application/json')
            else:
                user=User.objects.filter(id=empAdmin).get()
                print(user.id)
                #first hashing the password
                password=make_password(password,5)
                #creating the employee with provided details and saving
                employee=Employee.objects.create(fname=firstname,lname=lastname,email=email,password=password,street=street,pincode=pincode,country=country,mobileNumber=mobileNumber,empAdmin=user)
                employee.save()
                return HttpResponse('{"status":200,"message":"Employee is registered Successfuly"}',content_type='application/json')
    else:
        return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')

#login for Employee
def loginEmployee(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    if all(k in finalRequest for k in ('email','password')):

        email=request.POST['email']
        password=request.POST['password']

        #check field is set of not
        if email and password:
            print("all variables are set")
        else:
            return HttpResponse(
                '{"status":400,"message":"All Fields are mandatory"}',
                content_type='application/json'
            )

        #fetch the given email from the db to if it exists then check for password else return error
        if Employee.objects.filter(email=email).exists():
            allInfo=Employee.objects.filter(email=email).get()
            #check whether the given password matches with the hashed password or not
            passwordTest=check_password(password,allInfo.password)
            print(passwordTest)
            if passwordTest:
                return HttpResponse('{"status":200,"message":"User login successfuly."}',content_type='application/json')
            else:
                return HttpResponse('{"status":400,"message":"Password does not matches.Please check once again."}',content_type='application/json')
        else:
            return HttpResponse('{"status":400,"message":"Email does not exist in the DB.Please check once again."}',content_type='application/json')
        
##################################################################################################################

#saving possible worklocation of employees. Creating by User
def saveWorkLocation(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    if all(k in finalRequest for k in ('address','pincode','country','state','initialLongitude','initialLatitude','finalLongitude','finalLatitude')):
        address=request.POST['address']
        pincode=request.POST['pincode']
        country=request.POST['country']
        state=request.POST['state']
        initialLongitude=request.POST['initialLongitude']
        initialLatitude=request.POST['initialLatitude']
        finalLongitude=request.POST['finalLongitude']
        finalLatitude=request.POST['finalLatitude']

        #check field is set of not
        if address and pincode and country and state and initialLongitude and initialLatitude and finalLongitude and finalLatitude:
            print("all variables are set")
        else:
            return HttpResponse(
                '{"status":400,"message":"Required Fields cannot be empty"}',
                content_type='application/json'
            )

        #validating address
        if len(address) < 8:
            return HttpResponse(
                '{"status":400,"message":"Address length should have minimum length of 8"}',
                content_type='application/json'
            )

        #validating pincode
        if len(address) != 6:
            return HttpResponse(
                '{"status":400,"message":"Pincode length should have minimum length of 6"}',
                content_type='application/json'
            )

        #check if combination of location and pincode is already exist in the database
        if WorkLocations.objects.filter(initialLatitude=initialLatitude,initialLongitude=initialLongitude,finalLatitude=finalLatitude,finalLongitude=finalLongitude,pincode=pincode).exists():
            return HttpResponse(
                '{"status":400,"message":"Given location is already exists in the DB"}',
                content_type='application/json'
            )


        #by default active worklocation is created
        workloc=WorkLocations.objects.create(address=address,pincode=pincode,country=country,state=state,initialLatitude=initialLatitude,initialLongitude=initialLongitude,finalLatitude=finalLatitude,finalLongitude=finalLongitude)
        workloc.save()
        return HttpResponse('{"status":200,"message":"WorkLocation created successfuly."}',content_type='application/json')
    else:
        return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')


#saving employees current worklocations
def saveEmployeeCurrentLocation(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    if all(k in finalRequest for k in ('currentLongitude','currentLatitude','empId','workLocationId')):

        currentLongitude=request.POST['currentLongitude']
        currentLatitude=request.POST['currentLatitude']
        empId=request.POST['empId']
        workLocationId=request.POST['workLocationId']

        #check field is set of not
        if currentLongitude and currentLatitude and empId and workLocationId:
            print("all variables are set")
        else:
            return HttpResponse(
                '{"status":400,"message":"Required Fields cannot be empty"}',
                content_type='application/json'
            )

        #checking if empId is exist in the database or not
        emp=Employee.objects.filter(id=empId).get()
        print(emp.id)
        if not Employee.objects.filter(id=empId).exists():
            return HttpResponse('{"status":400,"message":"Employee Id is wrong"}',content_type='application/json')
        
        #checking if worklocation id is correct or not
        workLoc=WorkLocations.objects.filter(id=workLocationId).get()
        print(workLoc)
        if not WorkLocations.objects.filter(id=workLocationId).exists():
            return HttpResponse('{"status":400,"message":"WorkLocation Id is wrong"}',content_type='application/json')

        #saving successfuly
        empLoc=EmployeeWorkLocations.objects.create(empId=emp,workLocationId=workLoc,currentLatitude=currentLatitude,currentLongitude=currentLongitude)
        empLoc.save()
        return HttpResponse('{"status":200,"message":"Data Saved Successfuly"}',content_type='application/json')
    else:
        return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')


#saving employee image
class saveEmployeeImage(APIView):
    parser_classes = (MultiPartParser,)
    def post(self,request):

        file=request.data['file']
        print(file)
        finalRequest=request.data #QueryDict of all the request parameter in body
        print(finalRequest)

        if all(k in finalRequest for k in ('empId','file')):
            empId=request.data['empId']
            img=request.data['file']

            #check field is set of not
            if empId and img and empId :
                print("all variables are set")
            else:
                return HttpResponse(
                    '{"status":400,"message":"Required Fields cannot be empty"}',
                    content_type='application/json'
                )

            #checking if empId is valid or not
            emp=Employee.objects.filter(id=empId).get()
            print(emp.id)
            if not Employee.objects.filter(id=empId).exists():
                return HttpResponse('{"status":400,"message":"Employee Id is wrong"}',content_type='application/json')

            #saving image in DB
            empImg=EmployeeImages.objects.create(empId=emp,img=img)
            empImg.save()
            return HttpResponse('{"status":200,"message":"Data Saved Successfuly"}',content_type='application/json')
        else:
            return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')