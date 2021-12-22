from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView


from . import  views

urlpatterns=[
    path('',views.loginPage,name='loginPage'),
    path('signup',views.signupPage,name='signupPage'),
    path('registerUser',views.register,name='register'),
    path('user/<int:user_id>',views.user,name='user'),
    path('login',views.login,name='login'),
    path('user/<int:user_id>/update',views.update,name='update'),
    path('user/<int:user_id>/updation_<str:model>/<int:id>',views.updateInfo,name='updateInfo'),
    path('user/<int:user_id>/about',views.about,name='about'),
    path('user/<int:user_id>/<str:func>',views.userInfoUpdate,name='userInfoUpdate'),
    path('inactiveUser',views.inactiveUser,name='inactiveUser'),
    path('registerEmployee',views.registerEmployee,name='registerEmployee'),
    path('loginEmployee',views.loginEmployee,name='loginEmployee'),
    path('workLocation/<str:method>',views.newWorkLocation,name='newWorkLocation'),
    path('user/<int:user_id>/employee/<str:model>',views.employeeNew,name='employeeNew'),
    path('user/<int:user_id>/employee/<str:empId>/monthlypayroll',views.employeeMonthlyPayrol,name='employeeMonthlyPayrol'),
    path('users/<int:user_id>/mapWorkLocation',views.mapWorkLocation,name='mapWorkLocation'),
    path('user/<int:user_id>/list_all/<str:model>',views.list_all,name='list_all'),
    path('saveWorkLocation',views.saveWorkLocation,name='saveWorkLocation'),
    path('saveEmployeeCurrentLocation/<int:user_id>',views.saveEmployeeCurrentLocation,name='saveEmployeeCurrentLocation'),
    path('saveEmployeeImage',views.saveEmployeeImage.as_view(),name='saveEmployeeImage'),
    path('forgotPassword',views.forgotPassword,name='forgotPassword'),
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),

]

urlpatterns=urlpatterns + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)