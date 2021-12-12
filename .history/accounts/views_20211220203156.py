from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect, render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User,auth
from django.contrib.auth.hashers import make_password,check_password
from .models import Employee,WorkLocations,EmployeeWorkLocations,EmployeeImages,UserLoggedIn
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser,MultiPartParser 
import re
from datetime import datetime,timedelta,date
from django.utils import timezone
import folium
import geocoder
import array as arr
import random
import smtplib,ssl


####################################### User UI Part ##############################################3

#signup page for admin 
def signupPage(request):
    return render(request,'signup.html')

#login page for admin
def loginPage(request):
    return render(request,'login.html')

def user(request,user_id):
    if not request.user.is_authenticated:
        messages.error(request,'Please login first to continue')
        return redirect('/')
    print(user_id)
    #check if user has been authenticate by Super admin or not
    user=User.objects.filter(id=user_id).get()
    if user.is_staff:
        #if yes then show the infor
        pass
    else:
        #else show warning
        messages.warning(request,"You are not validate by Super Admin yet.Please contact Admin.")
        return redirect('/')
    return render(request,'home.html',{'user_id':user_id})

#to adding new location
def newWorkLocation(request,method):
    if method == 'new':
        g=geocoder.ip('me')#getting the mine ip
        print(g.address)
        lat=g.lat#getting latitude
        lng=g.lng#getting langitude
        #creating map
        m=folium.Map(location=[lat,lng],zoom_start=5)
        folium.Marker([lat,lng],tooltip='click for more',popup=g.address).add_to(m)#adding marker to the map
        #get html representation of map object
        m = m._repr_html_()
        context={
            'm':m,
        }
        
        return render(request,'addNewWorkLocation.html',context)
        
#to print all data of employe and worklocation
def list_all(request,user_id,model):
    if not request.user.is_authenticated:
        messages.error(request,'Please login first to continue')
        return redirect('/')
    print(model)
    #getall worklocations 
    allWorkLocations=WorkLocations.objects.all()
    print(allWorkLocations)

    #getall employees 
    allEmployee=Employee.objects.all().filter(empAdmin=user_id)
    print(allEmployee)

    empIds=[]

    if model == 'mapping':
        #get all mappings
        for eachEmployee in allEmployee:
            print(eachEmployee.id)
            empIds.append(eachEmployee.id)
            #fetching employee current location
            # employeeCurrentLocation=
            # print(employeeCurrentLocation)
            # empInfo.append(employeeCurrentLocation)

        empInfo=EmployeeWorkLocations.objects.all().filter(empId__in = empIds)
        print(empInfo)
        print("sf")
        return render(request,'list.html',{'workLocations':allWorkLocations,'employees':allEmployee,'model':model,'user_id':user_id,'empInfor':empInfo})
    
   
    
    return render(request,'list.html',{'workLocations':allWorkLocations,'employees':allEmployee,'model':model,'user_id':user_id})

#creating employee new
def employeeNew(request,user_id,model):
    if not request.user.is_authenticated:
        messages.error(request,'Please login first to continue')
        return redirect('/')
    if model == 'new':
        return render(request,'addNewEmployee.html',{'user_id':user_id})
    else:
       # date= datetime.date.today().strftime("%Y-%m-%d")
        currdate=date.today()
        empId=model.split('_')[1]
        if request.method == 'POST':
            print(request.POST['saveDateTime'])
            currdate=request.POST['saveDateTime']

        #fetching employee image
        # if not EmployeeImages.objects.filter(empId = empId).exists():
        #     messages.error(request,"There is no image of this employee yet.Please check after sometime")
        #     return render(request,'empInformation.html',{'user_id':user_id})

        if date is not None:
            print(currdate)
            employeeImages=EmployeeImages.objects.filter(empId = empId,saveDateTime__startswith=currdate)
            print(employeeImages)
            if employeeImages.exists():
                employeeImages=employeeImages.get()
            else:
                messages.error(request,"There is no image for this date of this employee yet.Please check after sometime")
                return render(request,'empInformation.html',{'user_id':user_id,'empId':empId,'currdate':currdate})
            #get current location
            employeeCurrentLocation=EmployeeWorkLocations.objects.filter(empId = empId,updated_at__startswith=currdate)
            if employeeCurrentLocation.exists():
                employeeCurrentLocation=employeeCurrentLocation.get()
            else:
                messages.error(request,"There is no location for this date of this employee yet.Please check after sometime")
                return render(request,'empInformation.html',{'user_id':user_id,'empId':empId,'empImgs':employeeImages,'currdate':currdate})
            

        else:
            employeeImages=EmployeeImages.objects.filter(empId = empId).order_by('-saveDateTime')[0]
            print(employeeImages.id)
            #get current location
            employeeCurrentLocation=EmployeeWorkLocations.objects.filter(empId = empId).order_by('-updated_at')[0]
            print(employeeCurrentLocation.currenLatitude)


        
        g=geocoder.ip('me')#getting the mine ip
        # print(g.lat)
        # print(g.lng)
        lat=employeeCurrentLocation.currenLatitude#getting latitude
        lng=employeeCurrentLocation.currenLongitude#getting langitude
        # print(lat)
        # print(lng)
        #creating map
        m=folium.Map(location=[lat,lng],zoom_start=5)
        folium.Marker([lat,lng],tooltip='click for more',popup=employeeCurrentLocation.workLocationId.address).add_to(m)#adding marker to the map
        #get html representation of map object
        m = m._repr_html_()

        #fetching worklocation latitude and longitude for checking if employee works in same place or not
        workLatitude=employeeCurrentLocation.workLocationId.initialLatitude
        workLongitude=employeeCurrentLocation.workLocationId.initialLongitude

        #diff between both
        latdiff=lat-workLatitude
        longdiff=lng-workLongitude
        print(latdiff)
        print(longdiff)



        return render(request,'empInformation.html',{'user_id':user_id,'m':m,'empId':empId,'empImgs':employeeImages,'currdate':currdate})



#mapping employee to worlocation
def mapWorkLocation(request,user_id):
    if not request.user.is_authenticated:
        messages.error(request,'Please login first to continue')
        return redirect('/')
     #getall worklocations 
    allWorkLocations=WorkLocations.objects.all().filter(active=True)
    print(allWorkLocations)

    #getall employees 
    allEmployee=Employee.objects.all().filter(empAdmin=user_id,active=True)
    print(allEmployee)
    return render(request,'mapEmpToWork.html',{'workLocations':allWorkLocations,'employees':allEmployee,'user_id':user_id})

#print about page
def about(request,user_id):
    return render(request,'about.html',{'user_id':user_id})

#for changing password and update user information
def userInfoUpdate(request,user_id,func):
    #check if logged in or not
    if not request.user.is_authenticated:
        messages.error(request,'Please login first to continue')
        return redirect('/')

    userInfor=User.objects.all().filter(id=user_id).get()
    print(userInfor)
    if func == 'updateUserInfo':
        return render(request,'userInformation.html',{'user_id':user_id,'userInfor':userInfor,'func':func})

    elif func == 'changePassword':
        if request.method == 'GET':
            return render(request,'userInformation.html',{'user_id':user_id,'userInfor':userInfor,'func':func})

        opassword=request.POST['oldpassword']
        npassword=request.POST['password']
        npassword2=request.POST['newpassword2']

        #checking if old password matches
        passwordTest=check_password(opassword,userInfor.password)
        print(passwordTest)
        if passwordTest:
            if len(npassword) < 8:
             #setting the error message and redirect to signup page
                messages.error(request,"Password length should have minimum length of 8")
                return render(request,'userInformation.html',{'user_id':user_id,'userInfor':userInfor,'func':func})
            else:
                if npassword ==  npassword2:
                    value=make_password(npassword)#making password
                    User.objects.filter(id=user_id).update(password=value)
                    messages.success(request,'Password changes successfuly')
                else:
                    messages.warning(request,'New Password and Confirm Password does not matches')
        else:
            messages.warning(request,'Old Password does not matches')

        return render(request,'userInformation.html',{'user_id':user_id,'userInfor':userInfor,'func':func})

    elif func == 'logout':
        messages.success(request,'User Logout Successfuly')
        return redirect('/logout')

#for updating employee and worklocation
def updateInfo(request,user_id,model,id):
    if model=='employee':
        data=Employee.objects.all().filter(id=id).get()
    if model == 'workLocation':
        data=WorkLocations.objects.all().filter(id=id).get()

    print(data)

    return render(request,'update.html',{'data':data,'user_id':user_id,'model':model})

#sending mail for forgetting password
def forgotPassword(request):
    fieldUpdated={}
    if request.method == 'GET':
        return render(request,'forgotPassword.html')

    elif request.method == 'POST':
        email=request.POST['email']
        #validating email using regular expression
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            print("Valid Email")
        else:
            messages.error(request,"Email should be in valid format")
            return redirect('/forgotPassword')
           

        #return if email is not valid
        if not User.objects.filter(email=email).exists():
            messages.error(request,'Email does not exist')
            return redirect('/forgotPassword')

        data=User.objects.filter(email=email)#check if email is valid or not
        print(data)

        #generate random number and save as a password 
        password=random.randrange(10000,99999999)
        #apply hash
        hashPassword=make_password(str(password))

        #saving to db
        fieldUpdated['password']=hashPassword
        User.objects.filter(email=email).update(**fieldUpdated)

        #send email
        
        port = 587  # For SSL
        smtp_server = "smtp.gmail.com"
        subject="Password reset Mail"
        body="Your new password is:"+str(password)+".\nPlease Login using this password and then update your password"

        #f formast'
        msg=f'Subject: {subject}\n\n{body}'

        with smtplib.SMTP(smtp_server, port) as smtp:

            smtp.ehlo()
            smtp.starttls()#login in encrypted mode
            smtp.ehlo()

            smtp.login(settings.EMAIL_ADDR, settings.EMAIL_PASS)#login to your email
            smtp.sendmail(settings.EMAIL_ADDR, email, msg) #send mail to user

        #returning to inform client that mail has been sent
        messages.info(request,'Email has been send to your email Id with password.Please check')
        return redirect('/')

def employeeMonthlyPayrol(request,user_id,empId):
    if request.method == 'POST':
        initialDate=request.POST['startTime']
        endDate=request.POST['endTime']
        print(initialDate)
        print(endDate)
        while initialDate<endDate:
            empInfo=dict()
            userPhoto=EmployeeImages.objects.filter(empId=empId,saveDateTime__startswith=initialDate)
            if userPhoto.exists():
                print(userPhoto.get().is_verified)
                empInfo['photoVerified']=userPhoto.get().is_verified
            else:
                empInfo['photoVerified']="N"
            userLocation=EmployeeWorkLocations.objects.filter(empId=empId,updated_at__startswith=initialDate)
            if userLocation.exists():
                first=True
                for eachLocation in userLocation:
                    if first:
                        empInfo['signIn']=eachLocation.updated_at.strftime("%Y-%m-%d %H:%M:%S") 
                        first=False

                    empInfo['signOff']=eachLocation.updated_at.strftime("%Y-%m-%d %H:%M:%S") 
            else:
                empInfo['time']=False
            print('----------------')
            print(empInfo)
            initialDate=datetime(initialDate).strftime("%Y-%m-%d")+timedelta(days=1)
            print(initialDate)
            return render(request,'EmployeePayrol.html',{'user_id':user_id,'empId':empId})
        
    else:
        return render(request,'EmployeePayrol.html',{'user_id':user_id,'empId':empId})
        

#################################################### User Admin CRUD operation Start ###################

#registerAdmin by HR using name email and password
def register(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict

    if all(k in finalRequest for k in ('first_name','last_name','username','email','password','confirmPassword')):
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
            #setting the error message and redirect to signup page
            messages.error(request,"Required Fields cannot be empty")
            return render(request,'signup.html')
            # return HttpResponse(
            #     '{"status":400,"message":"Required Fields cannot be empty"}',
            #     content_type='application/json'
            # )

        #validating email using regular expression
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            print("Valid Email")
        else:
            messages.error(request,"Email should be in valid format")
            return render(request,'signup.html')
            # return HttpResponse(
            #     '{"status":400,"message":"Email should be in valid format"}',
            #     content_type='application/json'
            # )

        #validating username length
        if len(username) < 8:
             #setting the error message and redirect to signup page
            messages.error(request,"Username length should have minimum length of 8")
            return render(request,'signup.html')
            # return HttpResponse(
            #     '{"status":400,"message":"Username length should have minimum length of 8"}',
            #     content_type='application/json'
            # )

        #validating password length
        if len(password1) < 8:
             #setting the error message and redirect to signup page
            messages.error(request,"Password length should have minimum length of 8")
            return render(request,'signup.html')
            # return HttpResponse(
            #     '{"status":400,"message":"Password length should have minimum length of 8"}',
            #     content_type='application/json'
            # )

        #checking if both the password is same or not
        if password1 == password2:
            #checking if username is already exist in DB
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username taken')
                 #setting the error message and redirect to signup page
                messages.error(request,"Username is taken")
                return render(request,'signup.html')
                # return HttpResponse('{"status":400,"message":"Username is taken."}',content_type='application/json')#returns an error

            else:
                #else creating the userAdmin with is_active true by default
                user=User.objects.create_user(username=username,first_name=firstname,last_name=lastname,email=email,password=password1)

                user.save()
                print('success')
                 #setting the error message and redirect to signup page
                messages.success(request,"User registered successfuly.Please login further.")
                return render(request,'login.html')
                # return HttpResponse('{"status":200,"message":"User registered successfuly."}',content_type='application/json')
        else:
            #if password does not matches then returns an error
             #setting the error message and redirect to signup page
            messages.error(request,"Password does not matches. Please check and Try again")
            return render(request,'signup.html')
            # return HttpResponse('{"status":400,"message":"Password does not matches. Please check and Try again"}',content_type='application/json')
    else:
         #setting the error message and redirect to signup page
            messages.error(request,"Required fields are missing in the request")
            return render(request,'signup.html')
        # return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')

#by default createUSer is not in staff first use to verify by superuser to make it as staff member


#login UserAdmin using username and password
def login(request):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict
    print(finalRequest)



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

        if not User.objects.filter(username=username).exists():
            messages.error(request,"Invalid Username.Please register yourself first.")
            return redirect('/')


        #authenticate the user using username and password 
        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            userId=user.id#saving user id

            print("inside success")

            #redirect to UI page with user id
            return redirect('/user'+'/{}'.format(userId))
            #return HttpResponse('{"status":200,"message":"User login successfuly."}',content_type='application/json')
        else:
            print("inside failure 1")
            messages.error(request,"Invalid password for given username.Please check once again.")
            return redirect('/')
    else:
        print("inside failue 2")
        messages.error(request,"Required Fields are missing in the request.")
        return redirect('/')
        #return HttpResponse('{"status":400,"message":"Required Fields are missing in the request."}',content_type='application/json')


#update operation in User and Employee and WorkLocation(reusability of same function)
def update(request,user_id):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict
    print(finalRequest)

    #updatioIn can be EMployee or User only
    if 'updationIn' in finalRequest and request.POST['updationIn'] in ['User','Employee','WorkLocations','EmployeeImages','EmployeeWorkLocations']:
        updatePerformedIn=request.POST['updationIn']
    else:
        messages.error(request,"updationIn is mandatory.Possible values are Employee and User only.")
        return redirect('/user/{}/list_all/{}'.format(user_id,'employees'))
       # return HttpResponse('{"status":400,"message":"updationIn is mandatory.Possible values are Employee and User only"}',content_type='application/json')

    if updatePerformedIn == 'WorkLocations':
        model = 'workLocation'
    elif updatePerformedIn == 'Employee':
        model='employees'
    elif updatePerformedIn == 'EmployeeImages':
        model='mapping'
    elif updatePerformedIn == 'User':
        model='user'
    elif updatePerformedIn == 'EmployeeWorkLocations':
        model='mapping'
    #checking if id is set in the request or else throw error
    if 'id' in finalRequest:
        userId=request.POST['id']
    else:
        messages.error(request,"Id is mandatory.")
        return redirect('/user/{}/list_all/{}'.format(user_id,model))
        # return HttpResponse('{"status":400,"message":"Id is mandatory"}',content_type='application/json')

    fieldToBeUpdated={}

    #constructing a dictionary of non empty value for updation
    for key,value in finalRequest.items():
        if value:
            if key == 'password':
                value=make_password(value)#before storing the password hashing first
                print(value)
            if key =='updationIn' or key == 'csrfmiddlewaretoken':#do nothing as updationKey is used for table only
                continue
            fieldToBeUpdated[key]=value

    print(fieldToBeUpdated)

    if updatePerformedIn=='User':
        User.objects.filter(id=userId).update(**fieldToBeUpdated)
    elif updatePerformedIn=='Employee':
        Employee.objects.filter(id=userId).update(**fieldToBeUpdated)
    elif updatePerformedIn=='WorkLocations':
        WorkLocations.objects.filter(id=userId).update(**fieldToBeUpdated)
    elif updatePerformedIn=='EmployeeImages':
        EmployeeImages.objects.filter(id=userId).update(**fieldToBeUpdated)
    elif updatePerformedIn=='EmployeeWorkLocations':
        EmployeeWorkLocations.objects.filter(id=userId).update(**fieldToBeUpdated)

    messages.success(request,"Information updated Successfuly.")
    if model=='user':
        return redirect('/user/{}/updateUserInfo'.format(user_id))
    else:
        return redirect('/user/{}/list_all/{}'.format(user_id,model))
    # return HttpResponse('{"status":200,"message":"Information updated Successfuly."}',content_type='application/json')


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
        state=request.POST['state']
        pincode=request.POST['pincode']
        country=request.POST['country']
        mobileNumber=request.POST['mobileNumber']
        empAdmin=request.POST['empAdmin']

        #check field is set of not
        if firstname and lastname and street and email and password and state and pincode and country and mobileNumber and empAdmin:
            print("all variables are set")
        else:
            # return HttpResponse(
            #     '{"status":400,"message":"Required Fields cannot be empty"}',
            #     content_type='application/json'
            # )
            messages.error(request,"Required Fields cannot be empty")
            return redirect('/user/{}/employee/new'.format(empAdmin))

        #validating email using regular expression
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            print("Valid Email")
        else:
            # return HttpResponse(
            #     '{"status":400,"message":"Email should be in valid format"}',
            #     content_type='application/json'
            # )
            messages.error(request,"Email should be in valid format")
            return redirect('/user/{}/employee/new'.format(empAdmin))

        #validating username length
        if len(pincode) < 6:
            # return HttpResponse(
            #     '{"status":400,"message":"Username length should have minimum length of 8"}',
            #     content_type='application/json'
            # )
            messages.error(request,"pincode length should have minimum length of 6")
            return redirect('/user/{}/employee/new'.format(empAdmin))

        #validating password length
        if len(password) < 8:
            # return HttpResponse(
            #     '{"status":400,"message":"Password length should have minimum length of 8"}',
            #     content_type='application/json'
            # )
            messages.error(request,"Password length should have minimum length of 8")
            return redirect('/user/{}/employee/new'.format(empAdmin))

        #checking if email already exist or not
        if Employee.objects.filter(email=email).exists():
            #return HttpResponse('{"status":400,"message":"Email already taken"}',content_type='application/json')
            messages.error(request,"Email already taken")
            return redirect('/user/{}/employee/new'.format(empAdmin))
        else:
            if not User.objects.filter(id=empAdmin).exists():
                #return HttpResponse('{"status":400,"message":"Employee Id is wrong"}',content_type='application/json')
                messages.error(request,"Employee Id is wrong")
                return redirect('/user/{}/employee/new'.format(empAdmin))
            else:
                user=User.objects.filter(id=empAdmin).get()
                print(user.id)
                #first hashing the password
                password=make_password(password,None,'md5')
                #creating the employee with provided details and saving
                employee=Employee.objects.create(fname=firstname,lname=lastname,email=email,password=password,street=street,pincode=pincode,state=state,country=country,mobileNumber=mobileNumber,empAdmin=user)
                employee.save()
                #return HttpResponse('{"status":200,"message":"Employee is registered Successfuly"}',content_type='application/json')
                messages.success(request,"Employee is registered Successfuly")
                return redirect('/user/{}/employee/new'.format(empAdmin))
    else:
       # return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')
        messages.error(request,"Required fields are missing in the request")
        return redirect('employee/new')

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

    print(finalRequest)
    if all(k in finalRequest for k in ('address','pincode','country','state')):
        g=geocoder.osm(request.POST['state'])#getting the mine ip
        print(g.address)
        lat=g.lat#getting latitude
        lng=g.lng#getting langitude
        address=request.POST['address']
        pincode=request.POST['pincode']
        country=request.POST['country']
        state=request.POST['state']
        initialLongitude=lng
        initialLatitude=lat
        finalLongitude=lng
        finalLatitude=lat

         #creating map
        m=folium.Map(location=[lat,lng],zoom_start=5)
        folium.Marker([lat,lng],tooltip='click for more',popup=g.address).add_to(m)#adding marker to the map
        #get html representation of map object
        m = m._repr_html_()

        #check field is set of not
        if address and pincode and country and state and initialLongitude and initialLatitude and finalLongitude and finalLatitude:
            print("all variables are set")
        else:
            # return HttpResponse(
            #     '{"status":400,"message":"Required Fields cannot be empty"}',
            #     content_type='application/json'
            # )
            messages.error(request,"Required Fields cannot be empty")
            return render(request,'addNewWorkLocation.html',{'m':m,})

        #validating address
        if len(address) < 8:
            # return HttpResponse(
            #     '{"status":400,"message":"Address length should have minimum length of 8"}',
            #     content_type='application/json'
            # )
            messages.error(request,"Address length should have minimum length of 8")
            return render(request,'addNewWorkLocation.html',{'m':m,})

        #validating pincode
        if len(pincode) != 6:
            # return HttpResponse(
            #     '{"status":400,"message":"Pincode length should have minimum length of 6"}',
            #     content_type='application/json'
            # )
            messages.error(request,"Pincode length should have minimum length of 6")
            return render(request,'addNewWorkLocation.html',{'m':m,})


        #check if combination of location and pincode is already exist in the database
        if WorkLocations.objects.filter(initialLatitude=initialLatitude,initialLongitude=initialLongitude,finalLatitude=finalLatitude,finalLongitude=finalLongitude,pincode=pincode).exists():
            # return HttpResponse(
            #     '{"status":400,"message":"Given location is already exists in the DB"}',
            #     content_type='application/json'
            # )
            messages.error(request,"Given location is already exists in the DB")
            return render(request,'addNewWorkLocation.html',{'m':m,})



        #by default active worklocation is created
        workloc=WorkLocations.objects.create(address=address,pincode=pincode,country=country,state=state,initialLatitude=initialLatitude,initialLongitude=initialLongitude,finalLatitude=finalLatitude,finalLongitude=finalLongitude)
        workloc.save()
        messages.success(request,"WorkLocation created successfuly")
        return render(request,'addNewWorkLocation.html',{'m':m,})

        #return HttpResponse('{"status":200,"message":"WorkLocation created successfuly."}',content_type='application/json')
    else:
        #return HttpResponse('{"status":400,"message":"Required fields are missing in the request"}',content_type='application/json')
        messages.error(request,"Required fields are missing in the request")
        return render(request,'addNewWorkLocation.html')



#saving employees current worklocations
def saveEmployeeCurrentLocation(request,user_id):
    finalRequest=request.POST #QueryDict of all the request parameter in body
    finalRequest=finalRequest.dict()#changing dictionary from Query dict
    print(finalRequest)

    empId=request.POST['empId']
    workLocationId=request.POST['workLocationId']

    workLoc=WorkLocations.objects.filter(id=workLocationId).get()
    currentLongitude=workLoc.initialLongitude
    currentLatitude=workLoc.initialLatitude

        #check field is set of not
    if currentLongitude and currentLatitude and empId and workLocationId:
        print("all variables are set")
    else:
            # return HttpResponse(
            #     '{"status":400,"message":"Required Fields cannot be empty"}',
            #     content_type='application/json'
            # )
        messages.error(request,"Required Fields cannot be empty")
        return redirect('/users/{}/mapWorkLocation'.format(user_id))        

        #checking if empId is exist in the database or not
    emp=Employee.objects.filter(id=empId).get()
    print(emp.id)
    if not Employee.objects.filter(id=empId).exists():
            #return HttpResponse('{"status":400,"message":"Employee Id is wrong"}',content_type='application/json')
        messages.error(request,"Employee Id is wrong")
        return redirect('/users/{}/mapWorkLocation'.format(user_id))        
        
        #checking if worklocation id is correct or not
    workLoc=WorkLocations.objects.filter(id=workLocationId).get()
    print(workLoc)
    if not WorkLocations.objects.filter(id=workLocationId).exists():
            #return HttpResponse('{"status":400,"message":"WorkLocation Id is wrong"}',content_type='application/json')
        messages.error(request,"WorkLocation Id is wrong")
        return redirect('/users/{}/mapWorkLocation'.format(user_id))        

        #saving successfuly
    empLoc=EmployeeWorkLocations.objects.create(empId=emp,workLocationId=workLoc,currenLatitude=currentLatitude,currenLongitude=currentLongitude)
    empLoc.save()
     #return HttpResponse('{"status":200,"message":"Data Saved Successfuly"}',content_type='application/json')
    messages.success(request,"Data Saved Successfuly")
    return redirect('/users/{}/mapWorkLocation'.format(user_id))        
        


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