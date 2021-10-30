from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from . import  views

urlpatterns=[
    path('',views.registerView,name='registerView'),
    path('registerUser',views.register,name='register'),
    path('login',views.login,name='login'),
    path('update',views.update,name='update'),
    path('inactiveUser',views.inactiveUser,name='inactiveUser'),
    path('registerEmployee',views.registerEmployee,name='registerEmployee'),
    path('loginEmployee',views.loginEmployee,name='loginEmployee'),
    path('saveWorkLocation',views.saveWorkLocation,name='saveWorkLocation'),
    path('saveEmployeeCurrentLocation',views.saveEmployeeCurrentLocation,name='saveEmployeeCurrentLocation'),
    path('saveEmployeeImage',views.saveEmployeeImage.as_view(),name='saveEmployeeImage')
]

urlpatterns=urlpatterns + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)