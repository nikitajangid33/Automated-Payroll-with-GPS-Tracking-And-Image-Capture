from django.urls import path


from . import  views

urlpatterns=[
    path('',views.registerView,name='registerView'),
    path('registerUser',views.register,name='register'),
    path('login',views.login,name='login'),
    path('registerEmployee',views.registerEmployee,name='registerEmployee'),
    path('saveWorkLocation',views.saveWorkLocation,name='saveWorkLocation'),
    path('saveEmployeeCurrentLocation',views.saveEmployeeCurrentLocation,name='saveEmployeeCurrentLocation'),
    path('saveEmployeeImage',views.saveEmployeeImage,name='saveEmployeeImage')
]